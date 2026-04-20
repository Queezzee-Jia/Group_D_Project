import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import os

# Uncomment the following lines if you are debugging from mainland China and need a proxy.
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'


def _format_ticker(ticker: str) -> str:
    """
    Format stock ticker symbols.
    HK stocks (pure digits) are zero-padded to 4 digits and suffixed with .HK.
    Other tickers (e.g. US stocks) are returned unchanged.
    """
    if ticker.isdigit():
        return f"{ticker.zfill(4)}.HK"
    return ticker


def _get_price_from_history(stock: yf.Ticker) -> tuple[float, float] | tuple[None, None]:
    """
    Fallback price retrieval using historical data (period='5d').
    Uses the latest closing price as current price,
    and the second-to-last closing price as previous close.
    Returns (current_price, previous_close) or (None, None) on failure.
    """
    try:
        hist = stock.history(period="5d")
        if hist.empty or len(hist) < 1:
            return None, None

        current_price = round(float(hist["Close"].iloc[-1]), 2)

        if len(hist) >= 2:
            previous_close = round(float(hist["Close"].iloc[-2]), 2)
        else:
            # Only one row available; use the same value for both fields
            previous_close = current_price

        return current_price, previous_close

    except Exception as e:
        print(f"⚠️ Warning: History fallback failed. Reason: {e}")
        return None, None


def get_stock_price(ticker: str) -> dict | None:
    """
    Fetch real-time price and basic information for a single stock.

    Uses a three-layer fallback strategy to maximise reliability,
    especially for HK stocks where info dict is often incomplete:
        Layer 1 — stock.info        (fast but unstable on HK stocks)
        Layer 2 — stock.fast_info   (lightweight, partially reliable)
        Layer 3 — stock.history     (most reliable fallback)

    Returns a standardised dictionary with the following fields:
        ticker        (str)   : Formatted ticker symbol
        name          (str)   : Company name
        current_price (float) : Latest price
        previous_close(float) : Previous closing price
        change        (float) : Price change (current - previous)
        change_pct    (float) : Percentage change relative to previous close
        timestamp     (str)   : Time of data retrieval (YYYY-MM-DD HH:MM:SS)

    Returns None if all fallback layers fail.
    """
    formatted_ticker = _format_ticker(ticker)

    try:
        stock = yf.Ticker(formatted_ticker)

        current_price = None
        previous_close = None
        name = formatted_ticker  # Default to ticker symbol if name is unavailable

        # -------- Layer 1: stock.info --------
        try:
            info = stock.info
            if info:
                current_price = (
                    info.get("currentPrice")
                    or info.get("regularMarketPrice")
                )
                previous_close = info.get("previousClose")
                name = info.get("longName") or info.get("shortName") or formatted_ticker
        except Exception as e:
            print(f"⚠️ Warning: info fetch failed for {formatted_ticker}. Reason: {e}")

        # -------- Layer 2: stock.fast_info --------
        if current_price is None or previous_close is None:
            try:
                fast = stock.fast_info
                if current_price is None and fast.last_price:
                    current_price = round(float(fast.last_price), 2)
                if previous_close is None and fast.previous_close:
                    previous_close = round(float(fast.previous_close), 2)
            except Exception as e:
                print(f"⚠️ Warning: fast_info fetch failed for {formatted_ticker}. Reason: {e}")

        # -------- Layer 3: stock.history fallback --------
        if current_price is None or previous_close is None:
            print(f"ℹ️ Info: Falling back to history data for {formatted_ticker}.")
            hist_price, hist_prev = _get_price_from_history(stock)
            if current_price is None:
                current_price = hist_price
            if previous_close is None:
                previous_close = hist_prev

        # -------- Final validation --------
        if current_price is None or previous_close is None:
            raise ValueError(
                f"All fallback layers failed. Could not retrieve price for {formatted_ticker}."
            )

        # Calculate price change and percentage change for downstream members
        change = round(current_price - previous_close, 2)
        change_pct = (
            round((change / previous_close) * 100, 2)
            if previous_close != 0
            else 0.0
        )

        return {
            "ticker": formatted_ticker,
            "name": str(name),
            "current_price": round(float(current_price), 2),
            "previous_close": round(float(previous_close), 2),
            "change": change,
            "change_pct": change_pct,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        print(f"⚠️ Warning: Failed to fetch data for stock {formatted_ticker}. Reason: {e}")
        return None


def get_multiple_stocks(tickers: list) -> list:
    """
    Batch fetch data for multiple stocks.
    Failed tickers are automatically filtered out from the result.
    A short delay is added between requests to avoid hitting rate limits.

    Args:
        tickers (list): List of ticker symbols (HK digits or US symbols).

    Returns:
        list: List of standardised stock dictionaries (failed tickers excluded).
    """
    results = []
    for ticker in tickers:
        data = get_stock_price(ticker)
        if data is not None:
            results.append(data)
        # Brief pause between requests to respect API rate limits
        time.sleep(0.5)
    return results


def get_stock_history(ticker: str, period: str = "7d") -> pd.DataFrame | None:
    """
    Fetch historical OHLCV price data for charting purposes.
    Primarily used by the visualisation module (Member 4).

    Args:
        ticker (str) : Ticker symbol (HK digits auto-formatted to XXXX.HK).
        period (str) : Data period string accepted by yfinance
                       e.g. "1d", "5d", "1mo", "3mo", "1y". Default is "7d".

    Returns:
        pd.DataFrame : DataFrame containing Open, High, Low, Close, Volume columns.
        None         : If data is unavailable or an error occurs.
    """
    formatted_ticker = _format_ticker(ticker)
    try:
        stock = yf.Ticker(formatted_ticker)
        hist = stock.history(period=period)

        if hist.empty:
            raise ValueError(f"No historical data returned for {formatted_ticker} over period '{period}'.")

        return hist

    except Exception as e:
        print(f"⚠️ Warning: Failed to fetch historical data for stock {formatted_ticker}. Reason: {e}")
        return None