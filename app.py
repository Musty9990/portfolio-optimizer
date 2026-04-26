"""
Portfolio Optimizer — Streamlit Web App
========================================
Interactive Modern Portfolio Theory (Markowitz) tool.

Run with:
    streamlit run app.py
"""

import logging
from datetime import datetime

import streamlit as st

from core.data_fetcher import fetch_price_data, DataFetchError
from core.optimizer import (
    optimize_max_sharpe,
    optimize_min_volatility,
    generate_efficient_frontier,
)
from core.visualizer import (
    plot_efficient_frontier,
    plot_allocation_pie,
    plot_price_history,
)
from utils.exporters import export_to_excel


# --- Page configuration ---
st.set_page_config(
    page_title="Portfolio Optimizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# --- Header ---
st.title("📊 Portfolio Optimizer")
st.markdown(
    "**Modern Portfolio Theory (Markowitz)** — Find the optimal asset allocation "
    "based on historical price data. Supports US stocks and BIST (`.IS` suffix)."
)
st.divider()


# --- Sidebar: User inputs ---
with st.sidebar:
    st.header("⚙️ Configuration")

    preset = st.selectbox(
        "Quick presets",
        ["Custom", "US Tech (AAPL, MSFT, GOOGL, AMZN, NVDA)",
         "US Diversified (SPY, AGG, GLD, VNQ, EEM)",
         "BIST Banks (GARAN.IS, AKBNK.IS, ISCTR.IS, YKBNK.IS)"],
    )

    preset_map = {
        "Custom": "AAPL, MSFT, GOOGL",
        "US Tech (AAPL, MSFT, GOOGL, AMZN, NVDA)": "AAPL, MSFT, GOOGL, AMZN, NVDA",
        "US Diversified (SPY, AGG, GLD, VNQ, EEM)": "SPY, AGG, GLD, VNQ, EEM",
        "BIST Banks (GARAN.IS, AKBNK.IS, ISCTR.IS, YKBNK.IS)": "GARAN.IS, AKBNK.IS, ISCTR.IS, YKBNK.IS",
    }

    tickers_input = st.text_area(
        "Tickers (comma-separated)",
        value=preset_map[preset],
        help="Use Yahoo Finance symbols. BIST stocks need `.IS` suffix (e.g., GARAN.IS).",
        height=80,
    )

    period = st.select_slider(
        "Historical period",
        options=["6mo", "1y", "2y", "3y", "5y", "10y"],
        value="2y",
    )

    risk_free_rate = st.slider(
        "Risk-free rate (annual)",
        min_value=0.0, max_value=0.20, value=0.02, step=0.005,
        format="%.3f",
        help="Used in Sharpe ratio calculation. Default: 2%.",
    )

    n_frontier_points = st.slider(
        "Frontier resolution",
        min_value=10, max_value=100, value=40, step=5,
    )

    st.divider()
    optimize_btn = st.button("🚀 Optimize Portfolio", type="primary", use_container_width=True)


# --- Main panel ---
if optimize_btn:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    if len(tickers) < 2:
        st.error("⚠️ Please provide at least 2 tickers.")
        st.stop()

    with st.spinner(f"Fetching data for {len(tickers)} tickers..."):
        try:
            prices = fetch_price_data(tickers, period=period)
        except DataFetchError as e:
            st.error(f"❌ Data fetch failed: {e}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.stop()

    if prices.shape[1] < 2:
        st.error(f"⚠️ Only {prices.shape[1]} valid ticker(s). Need at least 2.")
        st.stop()

    st.success(
        f"✅ Loaded {prices.shape[0]} days × {prices.shape[1]} assets "
        f"({prices.index.min().date()} → {prices.index.max().date()})"
    )

    # --- Optimization ---
    with st.spinner("Running Markowitz optimization..."):
        try:
            max_sharpe = optimize_max_sharpe(prices, risk_free_rate=risk_free_rate)
            min_vol = optimize_min_volatility(prices)
            frontier = generate_efficient_frontier(prices, n_points=n_frontier_points)
        except Exception as e:
            st.error(f"❌ Optimization failed: {e}")
            st.stop()

    # --- KPI metrics ---
    st.subheader("📌 Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Max Sharpe Return", f"{max_sharpe.expected_return*100:.2f}%")
    c2.metric("Max Sharpe Volatility", f"{max_sharpe.volatility*100:.2f}%")
    c3.metric("Max Sharpe Ratio", f"{max_sharpe.sharpe_ratio:.3f}")
    c4.metric("Min Vol Return", f"{min_vol.expected_return*100:.2f}%")

    st.divider()

    # --- Charts ---
    st.subheader("📈 Efficient Frontier")
    if not frontier.empty:
        st.plotly_chart(
            plot_efficient_frontier(frontier, max_sharpe, min_vol),
            use_container_width=True,
        )
    else:
        st.warning("Frontier generation failed — try a different ticker set.")

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("⭐ Max Sharpe Allocation")
        st.plotly_chart(
            plot_allocation_pie(max_sharpe, "Max Sharpe Portfolio"),
            use_container_width=True,
        )
    with col_right:
        st.subheader("🛡️ Min Volatility Allocation")
        st.plotly_chart(
            plot_allocation_pie(min_vol, "Min Volatility Portfolio"),
            use_container_width=True,
        )

    st.subheader("📉 Price History (Indexed to 100)")
    st.plotly_chart(plot_price_history(prices), use_container_width=True)

    # --- Detailed weights tables ---
    st.divider()
    st.subheader("📋 Detailed Weights")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Max Sharpe**")
        ms_df = (
            {"Ticker": list(max_sharpe.weights.keys()),
             "Weight (%)": [round(w * 100, 2) for w in max_sharpe.weights.values()]}
        )
        st.dataframe(ms_df, use_container_width=True, hide_index=True)
    with col_b:
        st.markdown("**Min Volatility**")
        mv_df = (
            {"Ticker": list(min_vol.weights.keys()),
             "Weight (%)": [round(w * 100, 2) for w in min_vol.weights.values()]}
        )
        st.dataframe(mv_df, use_container_width=True, hide_index=True)

    # --- Excel export ---
    st.divider()
    st.subheader("💾 Export Report")
    excel_bytes = export_to_excel(max_sharpe, min_vol, prices, frontier)
    filename = f"PortfolioReport_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    st.download_button(
        label="📥 Download Excel Report",
        data=excel_bytes,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )

else:
    # Landing message
    st.info(
        "👈 Configure your portfolio in the sidebar and click **Optimize Portfolio**.\n\n"
        "**Tip:** Try one of the presets to get started, or enter your own tickers."
    )
    st.markdown("""
    ### What this tool does
    - 📥 **Fetches live historical prices** via Yahoo Finance
    - 📐 Computes **expected returns and covariance** (Markowitz inputs)
    - ⭐ Finds the **Max Sharpe portfolio** (best risk-adjusted return)
    - 🛡️ Finds the **Min Volatility portfolio** (lowest risk)
    - 📈 Plots the **Efficient Frontier** (set of optimal portfolios)
    - 💾 Exports a **multi-sheet Excel report**
    """)
