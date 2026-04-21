import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# --- Import all team modules ---
from stock_data_acquisition import get_multiple_stocks
from price_alert import calculate_change, check_alert
from data_processing import format_data_for_ui  # Refactored Member 2
from visualization import plot_price_trend, plot_realtime_bar  # Refactored Member 4

# --- Page Configuration ---
st.set_page_config(
    page_title="Pro Stock Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make the dashboard look cleaner
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: Control Center ---
with st.sidebar:
    st.title("⚙️ Terminal Settings")
    
    # Session state for dynamic watchlist management
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ["0700", "0005", "AAPL", "NVDA", "TSLA"]
    
    # Add new ticker
    new_ticker = st.text_input("Add Ticker (e.g., 9988, MSFT)").strip().upper()
    if st.button("➕ Add to Watchlist") and new_ticker:
        if new_ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_ticker)
            st.rerun()

    st.write("---")
    st.subheader("🚨 Alert Thresholds")
    up_threshold = st.number_input("Up Alert (%)", value=2.0, step=0.5)
    down_threshold = st.number_input("Down Alert (%)", value=-2.0, step=0.5)
    
    st.write("---")
    if st.button("🗑️ Clear Watchlist"):
        st.session_state.watchlist = []
        st.rerun()
        
    st.caption("Auto-refresh is handled by browser extensions if needed.")

# --- Main Dashboard ---
st.title("💹 Real-Time Market Terminal")

if not st.session_state.watchlist:
    st.info("ℹ️ Your watchlist is empty. Please add tickers from the sidebar.")
else:
    # 1. Fetch data (Member 1 logic)
    with st.spinner("Fetching live market data..."):
        raw_stocks_data = get_multiple_stocks(st.session_state.watchlist)

    if raw_stocks_data:
        # 2. Process Alerts (Member 3 logic)
        for stock in raw_stocks_data:
            calculated_stock = calculate_change(stock)
            alert = check_alert(calculated_stock, up_threshold, down_threshold)
            
            # Use Streamlit's native toast for real-time notification UX
            if alert == "UP":
                st.toast(f"{stock['name']} is UP by {calculated_stock['change_percent']:+.2f}%", icon="🚀")
            elif alert == "DOWN":
                st.toast(f"{stock['name']} is DOWN by {calculated_stock['change_percent']:+.2f}%", icon="📉")

        # --- Top Section: Key Metrics ---
        st.subheader("Top Performers (Watchlist)")
        # Sort data by change_percent descending to find top performers
        sorted_data = sorted(raw_stocks_data, key=lambda x: x['change_pct'], reverse=True)
        
        # Display top 4 items as metric cards
        metric_cols = st.columns(min(4, len(sorted_data)))
        for i in range(len(metric_cols)):
            stock = sorted_data[i]
            with metric_cols[i]:
                st.metric(
                    label=stock['ticker'] + " - " + stock['name'][:10],
                    value=f"{stock['current_price']:.2f}",
                    delta=f"{stock['change_pct']:+.2f}%"
                )

        st.write("---")

        # --- Middle Section: Data Table (Member 2) ---
        st.subheader("Live Market Table")
        # Call Member 2's refactored UI function to get a clean DataFrame
        df_ui = format_data_for_ui(raw_stocks_data)
        
        if not df_ui.empty:
            # Display DataFrame cleanly, occupying full width without index
            st.dataframe(df_ui, use_container_width=True, hide_index=True)
        
        st.write("---")

        # --- Bottom Section: Visualizations (Member 4) ---
        st.subheader("Market Visualizations")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("**Real-Time Price Comparison**")
            # Call Member 4's bar chart function
            bar_fig, details_text = plot_realtime_bar(st.session_state.watchlist)
            if bar_fig:
                st.pyplot(bar_fig)
                # Display the raw text details in an expander
                with st.expander("View Raw Data Details"):
                    st.text(details_text)
            else:
                st.warning("Could not generate bar chart.")

        with chart_col2:
            st.markdown("**Historical Trend (7 Days)**")
            selected_chart_ticker = st.selectbox(
                "Select a stock to view trend:", 
                st.session_state.watchlist,
                label_visibility="collapsed"
            )
            # Call Member 4's trend chart function
            trend_fig = plot_price_trend(selected_chart_ticker, period="7d")
            if trend_fig:
                st.pyplot(trend_fig)
            else:
                st.warning(f"No historical data available for {selected_chart_ticker}.")

        # --- Footer ---
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Provider: yfinance")
        
    else:
        st.error("Failed to retrieve data. Please check your network connection or proxy settings.")