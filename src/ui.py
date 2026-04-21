import streamlit as st
import pandas as pd
from src.stock_data_acquisition import get_multiple_stocks
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="HK Stock Monitor", layout="wide")
st.title("Hong Kong Stock Real-Time Price and Alert Tool")

# Watchlist
watchlist = ["0700", "0005", "1299", "9988"]

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    up_threshold = st.number_input("Up Alert Threshold (%)", value=2.0, step=0.5)
    down_threshold = st.number_input("Down Alert Threshold (%)", value=-2.0, step=0.5)
    if st.button("Refresh"):
        st.rerun()

# Fetch data
with st.spinner("Fetching real-time data..."):
    data_list = get_multiple_stocks(watchlist)

if not data_list:
    st.error("Failed to fetch data. Please check your network.")
else:
    # Display as DataFrame
    df = pd.DataFrame(data_list)
    df["change_pct"] = df["change_pct"].apply(lambda x: f"{x:+.2f}%")
    df["current_price"] = df["current_price"].apply(lambda x: f"{x:.2f}")
    
    st.subheader("Real-Time Prices")
    st.dataframe(df[["ticker", "name", "current_price", "change_pct", "timestamp"]], use_container_width=True)
    
    # Alerts
    st.subheader("Price Alerts")
    alerted = False
    for stock in data_list:
        pct = stock["change_pct"]
        if pct >= up_threshold:
            st.success(f"{stock['ticker']} {stock['name']} Up {pct:+.2f}% | Current: {stock['current_price']}")
            alerted = True
        elif pct <= down_threshold:
            st.error(f"{stock['ticker']} {stock['name']} Down {pct:+.2f}% | Current: {stock['current_price']}")
            alerted = True
    if not alerted:
        st.info("No stocks triggered price alerts")
    
    # Bar chart
    st.subheader("Price Change Percentage Chart")
    fig, ax = plt.subplots()
    names = [s["name"] for s in data_list]
    pcts = [s["change_pct"] for s in data_list]
    colors = ["red" if p < 0 else "green" for p in pcts]
    ax.bar(names, pcts, color=colors)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.set_ylabel("Change (%)")
    plt.xticks(rotation=45)
    st.pyplot(fig)

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
