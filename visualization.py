# ==========================================================
# Member 4: Data Visualization & Chart Display
# Task: Stock Price Trend Chart + Real-time Bar Chart
# Data Source: src/stock_data_acquisition.py
# Libraries: matplotlib, plotly
# Output path: C:/Users/65810/OneDrive - Hong Kong Baptist University/桌面/新建文件夹 (2)/Group_D_Project/
# ==========================================================

import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# Import data functions from member 1 (NO changes to teammate's code)
from src.stock_data_acquisition import get_stock_history, get_multiple_stocks

# Global settings
plt.rcParams["font.family"] = ["Microsoft YaHei", "Calibri"]
plt.rcParams["axes.unicode_minus"] = False
OUTPUT_PATH = "C:/Users/65810/OneDrive - Hong Kong Baptist University/桌面/新建文件夹 (2)/Group_D_Project/"

# Function 1: Plot stock price trend line with data labels
def plot_price_trend(ticker, period="7d"):
    df = get_stock_history(str(ticker), period)
    
    if df is None or df.empty:
        print("No historical data available")
        return

    plt.figure(figsize=(12, 5))
    plt.plot(df.index, df["Close"], marker="o", linewidth=2, color="#1f77b4", label="Closing Price")
    
    # Show data values on chart
    for x, y in zip(df.index, df["Close"]):
        plt.text(x, y, f"{y:.2f}", ha="center", va="bottom", fontsize=9)

    plt.title(f"{ticker} Stock Price Trend", fontsize=14)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Price (HKD)", fontsize=12)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH + "price_trend.png", dpi=300)
    plt.close()
    print("✅ Price trend chart saved to: " + OUTPUT_PATH + "price_trend.png")

# Function 2: Plot real-time bar chart with data labels
def plot_realtime_bar(tickers):
    ticker_str_list = [str(t) for t in tickers]
    data = get_multiple_stocks(ticker_str_list)
    
    if not data:
        print("No real-time data available")
        return

    names = [item["name"] for item in data]
    prices = [item["current_price"] for item in data]

    plt.figure(figsize=(11, 5))
    bars = plt.bar(names, prices, color="#ff7f0e")

    # Show price values on top of bars
    for bar, price in zip(bars, prices):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 5,
                 f"{price:.2f}", ha="center", va="bottom", fontsize=10)

    plt.title("Real-time Stock Price Comparison", fontsize=14)
    plt.ylabel("Current Price (HKD)", fontsize=12)
    plt.xticks(rotation=15, ha="right")
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH + "realtime_bar.png", dpi=300)
    plt.close()
    print("✅ Bar chart saved to: " + OUTPUT_PATH + "realtime_bar.png")

# Main execution
if __name__ == "__main__":
    print("📊 Member 4 Visualization Running...")
    plot_price_trend(700, "7d")
    plot_realtime_bar([700, 5, 1299, 941])
    print("🎉 All charts generated successfully!")