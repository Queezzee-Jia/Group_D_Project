# 1. 从 src 文件夹下的 stock_data_acquisition.py 中导入组员写好的函数
from src.stock_data_acquisition import get_multiple_stocks

def format_and_display_data(stock_data_list):
    """
    用来把组员获取到的数据漂亮地打印出来
    """
    if not stock_data_list:
        print("没有获取到任何有效的股票数据。")
        return

    # 打印表头
    print("=" * 90)
    print(f"{'股票代码':<10} | {'公司名称':<20} | {'昨收价':<10} | {'现价':<10} | {'涨跌额':<10} | {'涨跌幅(%)':<10}")
    print("-" * 90)
    
    # 遍历打印每一只股票的数据
    for stock in stock_data_list:
        ticker = stock['ticker']
        # 截断过长的名字
        name = stock['name'][:18] + ".." if len(stock['name']) > 20 else stock['name']
        prev_close = stock['previous_close']
        current = stock['current_price']
        change = stock['change']
        change_pct = stock['change_pct']
        
        change_sign = "+" if change > 0 else ""
        
        print(f"{ticker:<12} | "
              f"{name:<20} | "
              f"{prev_close:<11.2f} | "
              f"{current:<11.2f} | "
              f"{change_sign}{change:<11.2f} | "
              f"{change_sign}{change_pct:.2f}%")
              
    print("=" * 90)
    print(f"数据更新时间: {stock_data_list[0]['timestamp']}")


# 2. 程序的真正入口
if __name__ == "__main__":
    # 准备你要查询的股票代码列表 (美股和港股)
    my_stocks = ["AAPL", "MSFT", "TSLA", "0700", "09988"] 
    
    print("正在联网拉取股票数据，请稍候...\n")
    
    # 3. 调用组员的函数，把列表传进去，并将返回的结果存入变量 analyzed_data
    analyzed_data = get_multiple_stocks(my_stocks)
    
    # 4. 把得到的数据传给你自己写的打印函数
    format_and_display_data(analyzed_data)