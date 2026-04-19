# 港股/美股实时价格查询工具 - 数据获取模块 API 文档
 
**版本**：v1.0  
**更新日期**：2026-04-19  
**模块文件**：`member1_data.py`

---

## 1. 模块概述

本模块负责**从 Yahoo Finance 获取港股和美股的实时价格、历史数据**，并提供统一的接口供其他成员调用。

### 核心功能
- 支持单个股票和批量股票查询
- 自动处理港股股票代码（纯数字自动添加 `.HK`）
- 提供实时价格、昨收价、时间戳等关键字段
- 完善的异常处理机制
- 返回标准化字典格式，方便成员2进行数据处理

---

## 2. 安装依赖

```bash
pip install yfinance pandas
````

---

## 3. 主要函数说明

### 3.1 `get_stock_price(ticker: str) -> dict | None`

**功能**：获取单只股票的实时价格和基本信息

**参数**：

* `ticker` (str)：股票代码

  * 美股：直接传入，如 `"AAPL"`、`"TSLA"`
  * 港股：支持两种格式

    * `"0700"`（纯数字，函数会自动转为 `"0700.HK"`）
    * `"0700.HK"`（已带后缀）

**返回值**：
成功时返回字典，失败返回 `None`

```python
{
    'ticker': str,           # 标准化后的股票代码（如 "0700.HK"）
    'name': str,             # 股票名称（中文或英文）
    'current_price': float,  # 当前价格（保留2位小数）
    'previous_close': float, # 昨收价（保留2位小数）
    'timestamp': str         # 数据获取时间，格式 "YYYY-MM-DD HH:MM:SS"
}
```

**使用示例**：

```python
from member1_data import get_stock_price

# 示例1：港股（推荐写法）
result = get_stock_price("0700")        # 腾讯控股
result = get_stock_price("0700.HK")

# 示例2：美股
result = get_stock_price("AAPL")
result = get_stock_price("TSLA")

if result:
    print(result)
else:
    print("获取数据失败")
```

**异常处理**：

* 网络超时、API 限制、股票代码不存在等情况均会捕获并打印警告
* 返回 `None`，不会导致程序崩溃

---

### 3.2 `get_multiple_stocks(tickers: list) -> list`

**功能**：批量获取多只股票的数据

**参数**：

* `tickers` (list[str])：股票代码列表

**返回值**：
返回列表，每个元素是 `get_stock_price()` 返回的字典（失败的股票会自动过滤，不包含 `None`）

**使用示例**：

```python
from member1_data import get_multiple_stocks

watchlist = ["0700", "9988", "AAPL", "TSLA", "9999"]  # 9999是不存在的测试代码

data_list = get_multiple_stocks(watchlist)

print(f"成功获取 {len(data_list)} 只股票数据")
for stock in data_list:
    print(stock)
```

---

### 3.3 `get_stock_history(ticker: str, period: str = "7d") -> pandas.DataFrame | None`

**功能**：获取股票历史行情数据（供成员4可视化使用）

**参数**：

* `ticker` (str)：股票代码（自动处理港股）
* `period` (str)：时间周期，默认 "7d"。支持："1d", "5d", "7d", "1mo", "3mo", "6mo", "1y", "max"

**返回值**：

* 成功返回 `pandas.DataFrame`，包含 Open, High, Low, Close, Volume 等列
* 失败返回 `None`

**使用示例**（成员4可直接调用）：

```python
from member1_data import get_stock_history

df = get_stock_history("0700", period="7d")
if df is not None:
    print(df.tail())
    # 成员4可以直接用 df 画图
```

---

## 4. 数据字段详细说明

| 字段             | 类型    | 说明        | 示例值                    |
| -------------- | ----- | --------- | ---------------------- |
| ticker         | str   | 标准化股票代码   | "0700.HK"              |
| name           | str   | 股票完整名称    | "Tencent Holdings Ltd" |
| current_price  | float | 最新收盘/实时价格 | 468.80                 |
| previous_close | float | 前一交易日收盘价  | 465.20                 |
| timestamp      | str   | 数据获取时间    | "2026-04-19 09:45:32"  |

**注意**：

* `current_price` 和 `previous_close` 已四舍五入保留两位小数
* 港股价格单位为 **HKD**，美股为 **USD**

---

## 5. 错误处理与注意事项

1. **股票代码格式**

   * 港股强烈推荐使用纯数字形式（如 "0700"），函数会自动补 `.HK`
   * 如果已带 `.HK`，函数不会重复添加

2. **调用频率限制**

   * yfinance 是免费接口，**不要设置间隔小于 10 秒** 的高频调用
   * 建议监控间隔设为 **30~60 秒**（成员3参考）

3. **网络问题**

   * 函数内部已包含重试机制（简单版），但仍建议在主程序中做好整体异常捕获

4. **交易时间**

   * 港股交易时间：北京时间 9:30-12:00，13:00-16:00
   * 非交易时间返回的数据为最后收盘价

