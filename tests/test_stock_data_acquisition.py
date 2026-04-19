import sys
import os
import pandas as pd
import time
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# 添加项目 src 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from stock_data_acquisition import (
    get_stock_price,
    get_multiple_stocks,
    get_stock_history,
    _format_ticker
)

# ==================== Fixtures ====================

@pytest.fixture(autouse=True)
def rate_limit_delay():
    """每个测试前等待 2 秒，避免 Rate Limit(对单元测试影响很小)"""
    time.sleep(2)
    yield

# ==================== 单元测试（Mock，不依赖网络，推荐日常运行） ====================

def test_format_ticker_input_output():
# 正常港股
    assert _format_ticker("0700") == "0700.HK"
    assert _format_ticker("700") == "0700.HK"      # 补零后结果
    assert _format_ticker("5") == "0005.HK"        # 补零
    assert _format_ticker("0005") == "0005.HK"

    # 美股/其他 ticker 不变
    assert _format_ticker("AAPL") == "AAPL"
    assert _format_ticker("TSLA") == "TSLA"

    # 边缘入参
    assert _format_ticker("") == ""                # 空字符串
    assert _format_ticker("0700.HK") == "0700.HK"  # 已带后缀不重复
    assert _format_ticker("ABC123") == "ABC123"    # 非纯数字

@patch("stock_data_acquisition.yf.Ticker")
def test_get_stock_price_input_output_success(mock_ticker):
    """测试 get_stock_price 正常入参 → 出参结构、类型、字段完整性"""
    mock_info = {
        "currentPrice": 350.50,
        "previousClose": 348.00,
        "longName": "Tencent Holdings Limited"
    }
    mock_instance = MagicMock()
    mock_instance.info = mock_info
    mock_ticker.return_value = mock_instance

    result = get_stock_price("0700")   # 入参测试：港股代码
    assert result is not None
    assert isinstance(result, dict)
    assert result["ticker"] == "0700.HK"
    assert result["name"] == "Tencent Holdings Limited"
    assert isinstance(result["current_price"], float)
    assert isinstance(result["previous_close"], float)
    assert isinstance(result["timestamp"], str)
    # 出参合理性检查
    assert result["current_price"] > 0
    assert datetime.strptime(result["timestamp"], "%Y-%m-%d %H:%M:%S")

@patch("stock_data_acquisition.yf.Ticker")
def test_get_stock_price_fallback_logic(mock_ticker):
    """测试价格字段 fallback（currentPrice 不存在时使用其他字段）"""
    mock_info = {
        "regularMarketPrice": 220.75,
        "previousClose": 218.50
    }
    mock_instance = MagicMock()
    mock_instance.info = mock_info
    mock_ticker.return_value = mock_instance

    result = get_stock_price("AAPL")
    assert result is not None
    assert result["current_price"] == 220.75

@patch("stock_data_acquisition.yf.Ticker")
def test_get_stock_price_invalid_input(mock_ticker):
    """测试无效入参或异常时出参为 None"""
    mock_ticker.side_effect = Exception("Invalid ticker or network error")
    result = get_stock_price("INVALID_999")   # 入参：无效代码
    assert result is None

    result2 = get_stock_price("")             # 入参：空字符串
    assert result2 is None

def test_get_multiple_stocks_input_output():
    """测试 get_multiple_stocks 的入参列表 → 出参过滤逻辑"""
    with patch("stock_data_acquisition.get_stock_price") as mock_get:
        mock_get.side_effect = [
            {"ticker": "0700.HK", "current_price": 350.0},  # 成功
            None,                                            # 失败
            {"ticker": "AAPL", "current_price": 220.0},     # 成功
            None                                             # 失败
        ]
        results = get_multiple_stocks(["0700", "FAKE_999", "AAPL", "INVALID"])  # 多入参测试
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(item, dict) for item in results)
        assert all("ticker" in item for item in results)

@patch("stock_data_acquisition.yf.Ticker")
def test_get_stock_history_input_output(mock_ticker):
    """测试 get_stock_history 的入参（ticker + period）与出参 DataFrame"""
    mock_hist = pd.DataFrame({
        "Open": [100.0, 101.0],
        "High": [102.0, 103.0],
        "Low": [99.0, 100.0],
        "Close": [101.0, 102.0],
        "Volume": [1000, 1100]
    }, index=pd.date_range("2025-04-01", periods=2))
    
    mock_instance = MagicMock()
    mock_instance.history.return_value = mock_hist
    mock_ticker.return_value = mock_instance

    # 测试不同 period 入参
    df = get_stock_history("0700", period="5d")
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]  # yfinance 默认列

    df2 = get_stock_history("AAPL", period="1mo")   # 不同 period
    assert df2 is not None

@patch("stock_data_acquisition.yf.Ticker")
def test_get_stock_history_empty(mock_ticker):
    """测试历史数据为空时的出参处理"""
    mock_instance = MagicMock()
    mock_instance.history.return_value = pd.DataFrame()  # 空 DataFrame
    mock_ticker.return_value = mock_instance

    df = get_stock_history("INVALID", period="5d")
    assert df is None   # 源码中会 raise 并捕获返回 None

# ==================== 集成测试（真实网络，偶尔运行，带保护） ====================

def test_get_stock_price_integration():
    """集成测试：真实入参 → 出参（网络正常时）"""
    result = get_stock_price("0700")
    if result is None:
        pytest.skip("网络/代理/Rate Limit 问题，跳过集成测试（非代码错误）")
    assert isinstance(result, dict)
    assert result["ticker"] == "0700.HK"
    assert "current_price" in result and isinstance(result["current_price"], float)

def test_get_multiple_stocks_integration():
    """集成测试：批量入参过滤"""
    results = get_multiple_stocks(["0700", "FAKE_999", "AAPL"])
    if len(results) == 0:
        pytest.skip("网络问题，所有请求失败，跳过")
    assert isinstance(results, list)
    assert len(results) >= 1
    assert all(isinstance(item, dict) for item in results)

def test_get_stock_history_integration():
    """集成测试：历史数据入参与出参"""
    df = get_stock_history("0700", period="5d")
    if df is None:
        pytest.skip("网络/代理问题，跳过")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) > 0