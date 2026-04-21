import pandas as pd
from src.stock_data_acquisition import get_multiple_stocks

def format_data_for_ui(stock_data_list):
    """
    Format the raw stock data and convert it into a Pandas DataFrame.
    Instead of printing directly, it returns the DataFrame so that 
    UI frameworks (like Streamlit) can render it properly.
    """
    if not stock_data_list:
        return pd.DataFrame() # Return an empty DataFrame if no data

    formatted_list = []
    
    for stock in stock_data_list:
        # Truncate overly long company names for better UI display
        name = stock['name'][:18] + ".." if len(stock['name']) > 20 else stock['name']
        
        change = stock['change']
        change_pct = stock['change_pct']
        change_sign = "+" if change > 0 else ""
        
        # Build a dictionary for each row with formatted string values
        formatted_item = {
            "Ticker": stock['ticker'],
            "Company Name": name,
            "Prev Close": f"{stock['previous_close']:.2f}",
            "Current Price": f"{stock['current_price']:.2f}",
            "Change Amt": f"{change_sign}{change:.2f}",
            "Change (%)": f"{change_sign}{change_pct:.2f}%",
            "Timestamp": stock['timestamp']
        }
        formatted_list.append(formatted_item)
        
    return pd.DataFrame(formatted_list)


# Program entry point for standalone CLI testing
if __name__ == "__main__":
    my_stocks = ["AAPL", "MSFT", "TSLA", "0700", "09988"] 
    
    print("Fetching stock data from the network, please wait...\n")
    
    analyzed_data = get_multiple_stocks(my_stocks)
    
    # Get the formatted DataFrame and print it to the console
    result_df = format_data_for_ui(analyzed_data)
    
    if not result_df.empty:
        print("=" * 90)
        # to_string(index=False) hides the row numbers for a cleaner look
        print(result_df.to_string(index=False)) 
        print("=" * 90)
    else:
        print("No valid stock data retrieved.")