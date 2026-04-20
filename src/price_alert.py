import time
from datetime import datetime

from stock_data_acquisition import get_multiple_stocks


def calculate_change(stock: dict) -> dict:
    """
    Calculate price change amount and percentage for one stock item.
    Returns a new dictionary with computed fields.
    """
    current_price = float(stock["current_price"])
    previous_close = float(stock["previous_close"])

    change_amount = round(current_price - previous_close, 2)
    if previous_close == 0:
        change_percent = 0.0
    else:
        change_percent = round((change_amount / previous_close) * 100, 2)

    result = dict(stock)
    result["change_amount"] = change_amount
    result["change_percent"] = change_percent
    return result


def check_alert(stock: dict, up_threshold: float = 2.0, down_threshold: float = -2.0) -> str | None:
    """
    Return alert level text if stock reaches threshold.
    """
    change_percent = float(stock["change_percent"])
    if change_percent >= up_threshold:
        return "UP"
    if change_percent <= down_threshold:
        return "DOWN"
    return None


def format_alert_message(stock: dict, alert_level: str) -> str:
    """
    Build readable alert text for terminal display.
    """
    direction = "上涨" if alert_level == "UP" else "下跌"
    sign = "+" if stock["change_amount"] >= 0 else ""
    return (
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
        f"提醒: {stock['ticker']} {stock['name']} {direction}触发阈值 | "
        f"现价: {stock['current_price']:.2f} | 昨收: {stock['previous_close']:.2f} | "
        f"涨跌额: {sign}{stock['change_amount']:.2f} | 涨跌幅: {sign}{stock['change_percent']:.2f}%"
    )


def monitor_stocks(
    tickers: list[str],
    up_threshold: float = 2.0,
    down_threshold: float = -2.0,
    interval_seconds: int = 30,
    max_rounds: int | None = None,
) -> None:
    """
    Monitor multiple stocks in a loop and print alerts when threshold is reached.

    Args:
        tickers: List of stock codes, e.g. ["0700", "AAPL"].
        up_threshold: Alert when change_percent >= this value.
        down_threshold: Alert when change_percent <= this value.
        interval_seconds: Polling interval in seconds.
        max_rounds: Optional max loop rounds. None means infinite monitoring.
    """
    if not tickers:
        print("No tickers provided. Monitoring stopped.")
        return

    round_count = 0
    print(
        f"开始监控 {len(tickers)} 只股票，提醒阈值: "
        f"上涨 >= {up_threshold:.2f}% / 下跌 <= {down_threshold:.2f}%"
    )

    while True:
        round_count += 1
        print(f"\n--- 监控轮次 {round_count} ---")

        stocks = get_multiple_stocks(tickers)
        if not stocks:
            print("本轮未获取到有效股票数据。")
        else:
            for stock in stocks:
                calculated = calculate_change(stock)
                alert_level = check_alert(calculated, up_threshold, down_threshold)
                if alert_level:
                    print(format_alert_message(calculated, alert_level))
                else:
                    print(
                        f"{calculated['ticker']} {calculated['name']} "
                        f"涨跌幅 {calculated['change_percent']:+.2f}%（未触发提醒）"
                    )

        if max_rounds is not None and round_count >= max_rounds:
            print("达到设定轮次，监控结束。")
            break

        time.sleep(interval_seconds)


if __name__ == "__main__":
    # Example watch list: HK + US
    WATCH_LIST = ["0700", "0005", "AAPL", "TSLA"]

    # Demo mode: run 2 rounds to avoid endless loop during quick test.
    monitor_stocks(
        tickers=WATCH_LIST,
        up_threshold=2.0,
        down_threshold=-2.0,
        interval_seconds=30,
        max_rounds=2,
    )
