import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# get data from teammate module
from src.stock_data_acquisition import get_stock_history, get_multiple_stocks

plt.rcParams["font.family"] = ["Calibri"]
plt.rcParams["axes.unicode_minus"] = False
OUTPUT_PATH = "C:/Users/65810/OneDrive - Hong Kong Baptist University/桌面/新建文件夹 (2)/Group_D_Project/"


def print_data_fields_detail(fetched_data):
    print("\n" + "="*70)
    print("4. Stock Data Fields Detailed Output (Dynamic Fetched Data)")
    print("="*70)
    for item in fetched_data:
        print(f"Ticker         : {item['ticker']}")
        print(f"Name           : {item['name']}")
        print(f"Current_price  : {item['current_price']:.2f}")
        print(f"Previous_close : {item['previous_close']:.2f}")
        print(f"Timestamp      : {item['timestamp']}")
        print("-" * 60)


def plot_price_trend(ticker, period="7d"):
    df = get_stock_history(str(ticker), period)
    if df is None or df.empty:
        print("No historical data available")
        return

    plt.figure(figsize=(12, 5))
    plt.plot(df.index, df["Close"], marker="o", linewidth=2, color="#1f77b4", label="Closing Price")

    # Show data values ON THE CHART
    for date, price in zip(df.index, df["Close"]):
        plt.text(date, price, f"{price:.2f}", ha="center", va="bottom", fontsize=9)

    plt.title(f"{ticker} Stock Price Trend", fontsize=14)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Price (HKD)", fontsize=12)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH + "price_trend.png", dpi=300)
    plt.close()


def plot_realtime_bar(tickers):
    """Bar chart + show price data labels on top of bars"""
    ticker_str_list = [str(t) for t in tickers]
    # Dynamic fetch real data from teammate
    fetched_data = get_multiple_stocks(ticker_str_list)

    if not fetched_data:
        print("No real-time data")
        return

    # Step1: Print data fields in terminal (your required format)
    print_data_fields_detail(fetched_data)

    names = [item["name"] for item in fetched_data]
    prices = [item["current_price"] for item in fetched_data]

    plt.figure(figsize=(11, 5))
    bars = plt.bar(names, prices, color="#ff7f0e")

    # Step2: Show price data ON THE BAR CHART
    for bar, price in zip(bars, prices):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 2,
                 f"{price:.2f}", ha="center", va="bottom", fontsize=10)

    plt.title("Real-time Stock Price Comparison", fontsize=14)
    plt.ylabel("Current Price (HKD)", fontsize=12)
    plt.xticks(rotation=15, ha="right")
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH + "realtime_bar.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    print("Member 4 Visualization Running...")
    print("Dynamically fetching data from member 1 module...")

    plot_price_trend(700, "7d")
    plot_realtime_bar([700, 5, 1299, 941])
