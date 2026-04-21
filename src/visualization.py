import matplotlib.pyplot as plt
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from src.stock_data_acquisition import get_stock_history, get_multiple_stocks

# Set global plot parameters
plt.rcParams["font.family"] = ["sans-serif"] # Changed to a safer default font
plt.rcParams["axes.unicode_minus"] = False

def get_data_fields_detail_str(fetched_data):
    """
    Format the raw data fields into a string instead of printing them directly.
    Returns the formatted string.
    """
    if not fetched_data:
        return "No real-time data available."
        
    output = []
    output.append("\n" + "="*70)
    output.append("4. Stock Data Fields Detailed Output (Dynamic Fetched Data)")
    output.append("="*70)
    for item in fetched_data:
        output.append(f"Ticker         : {item['ticker']}")
        output.append(f"Name           : {item['name']}")
        output.append(f"Current_price  : {item['current_price']:.2f} USD")
        output.append(f"Previous_close : {item['previous_close']:.2f} USD")
        output.append(f"Timestamp      : {item['timestamp']}")
        output.append("-" * 60)
        
    return "\n".join(output)


def plot_price_trend(ticker, period="7d"):
    """
    Generate a historical price trend chart.
    Returns the Matplotlib Figure object instead of calling plt.show().
    """
    df = get_stock_history(str(ticker), period)
    if df is None or df.empty:
        return None

    # Use object-oriented Matplotlib approach
    fig, ax = plt.subplots(figsize=(12, 5))
    
    close_price = df["Close"]
    ax.plot(df.index, close_price, marker="o", linewidth=2, color="#1f77b4", label="Closing Price")
    
    prev_close_price = df["Close"].shift(1)
    ax.plot(df.index, prev_close_price, marker="s", linewidth=2, color="#d62728", label="Previous Closing Price")

    for date, price in zip(df.index, close_price):
        ax.text(date, price, f"{price:.2f}", ha="center", va="bottom", fontsize=9, color="#1f77b4")
    
    for date, price in zip(df.index, prev_close_price):
        if not pd.isna(price):
            ax.text(date, price, f"{price:.2f}", ha="center", va="top", fontsize=9, color="#d62728")

    ax.set_title(f"{ticker} Price Trend (Closing & Previous Closing)", fontsize=14)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price (USD)", fontsize=12)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    
    return fig # Important: Return the figure object


def plot_realtime_bar(tickers):
    """
    Generate a real-time price comparison bar chart.
    Returns a tuple containing (Figure object, details_string).
    """
    ticker_str_list = [str(t) for t in tickers]
    fetched_data = get_multiple_stocks(ticker_str_list)

    if not fetched_data:
        return None, "No real-time data"

    # Get formatted details string
    details_str = get_data_fields_detail_str(fetched_data)

    names = [item["name"] for item in fetched_data]
    prices = [item["current_price"] for item in fetched_data]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(names, prices, color="#ff7f0e")

    for bar, price in zip(bars, prices):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 2,
                 f"{price:.2f}", ha="center", va="bottom", fontsize=10)

    ax.set_title("Real-time Stock Price Comparison", fontsize=14)
    ax.set_ylabel("Current Price (USD)", fontsize=12)
    
    # Set xticks properly to avoid warnings
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=15, ha="right")
    
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    
    return fig, details_str # Return figure and text


if __name__ == "__main__":
    print("Member 4 Visualization Running in CLI mode...")
    print("Dynamically fetching data from member 1 module...")

    # Test trend plot
    trend_fig = plot_price_trend(700, "7d")
    if trend_fig:
        trend_fig.show() # Only call show() when running as main

    # Test bar plot
    bar_fig, text_details = plot_realtime_bar([700, 5, 1299, 941])
    print(text_details)
    if bar_fig:
        bar_fig.show()