import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import os

#我在内地调试代码需要使用vpn代理，如在hk的话可以注释8，9行
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'

def _format_ticker(ticker: str) -> str:
    """Helper function to format HK stock tickers automatically."""
    # If the ticker consists only of digits, automatically append the .HK suffix
    if ticker.isdigit():
        return f"{ticker.zfill(4)}.HK"
    return ticker

def get_stock_price(ticker: str) -> dict | None:
    """
    Fetch real-time price and basic information for a single stock.
    Returns a standardized dictionary or None on failure.
    """
    # Format the stock ticker
    formatted_ticker = _format_ticker(ticker)
    
    try:
        stock = yf.Ticker(formatted_ticker)
        info = stock.info
        
        # yfinance's info dictionary is sometimes unstable; use fallback strategy for current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        previous_close = info.get('previousClose')
        name = info.get('longName') or info.get('shortName') or formatted_ticker
        
        if current_price is None or previous_close is None:
            raise ValueError("Incomplete price data returned from yfinance")

        # Construct standardized dictionary, rounding floats to 2 decimal places
        return {
            'ticker': formatted_ticker,
            'name': str(name),
            'current_price': round(float(current_price), 2),
            'previous_close': round(float(previous_close), 2),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        # Catch network timeouts or invalid tickers, print a clear warning
        print(f"⚠️ Warning: Failed to fetch data for stock {formatted_ticker}. Reason: {e}")
        return None

def get_multiple_stocks(tickers: list) -> list:
    """
    Batch fetch data for multiple stocks. 
    Filters out failed tickers and respects API rate limits.
    """
    results = []
    # Loop through tickers and automatically filter out failed ones (None results)
    for ticker in tickers:
        data = get_stock_price(ticker)
        if data is not None:
            results.append(data)
        
        # Add a 0.5-second delay between calls to avoid hitting rate limits
        time.sleep(0.5)
        
    return results

def get_stock_history(ticker: str, period: str = "7d") -> pd.DataFrame | None:
    """
    Fetch historical price data for charting.
    Returns a pandas DataFrame containing OHLCV data or None on failure.
    """
    formatted_ticker = _format_ticker(ticker)
    try:
        stock = yf.Ticker(formatted_ticker)
        hist = stock.history(period=period)
        
        # Return the OHLCV data directly (primarily used by Member 4 for charting)
        if hist.empty:
            raise ValueError("No historical data available for this period")
            
        return hist
        
    except Exception as e:
        # Catch exceptions and print a clear warning
        print(f"⚠️ Warning: Failed to fetch historical data for stock {formatted_ticker}. Reason: {e}")
        return None
