"""Three-page Streamlit frontend for the lab's single-stock strategy."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from trading_strategy import (
    get_stock_data, calculate_moving_averages,
    identify_golden_cross, implement_strategy,
)

st.set_page_config(page_title="MSFT Strategy Lab", page_icon="📈", layout="wide")


@st.cache_data(ttl=3600)
def load_results():
    data = identify_golden_cross(calculate_moving_averages(get_stock_data("MSFT")))
    return data, implement_strategy(data)


st.sidebar.title("Strategy Lab")
st.sidebar.caption("COMP4145 · Lab 2")
page = st.sidebar.radio("Page", ["Price chart", "Trade statistics", "Detailed trades"])
st.sidebar.divider()
st.sidebar.markdown("**Microsoft · MSFT**\n\n5 years of daily prices\n\n50 / 200-day moving averages\n\n15% profit target · 60 calendar days")
if st.sidebar.button("Refresh market data"):
    load_results.clear()

st.title(page)
st.caption("Single-stock golden cross backtest · Microsoft (MSFT)")
try:
    with st.spinner("Loading Microsoft price history…"):
        data, trades = load_results()
except Exception as exc:
    st.error(f"Could not load market data: {exc}")
    st.info("Check your internet connection and use Refresh market data. Yahoo Finance may temporarily limit requests.")
    st.stop()

st.caption(f"Data coverage: {data.index[0]:%d %b %Y} – {data.index[-1]:%d %b %Y} · {len(data):,} daily observations · adjusted USD prices")

if page == "Price chart":
    fig = go.Figure()
    for column, label, color in [("Close", "MSFT close", "#2563eb"), ("MA50", "50-day MA", "#d97706"), ("MA200", "200-day MA", "#7c3aed")]:
        fig.add_trace(go.Scatter(x=data.index, y=data[column], name=label, mode="lines", line=dict(color=color, width=2)))
    for date, price, label, color in [("BuyDate", "BuyPrice", "Buy", "#16a34a"), ("SellDate", "SellPrice", "Sell", "#dc2626")]:
        fig.add_trace(go.Scatter(x=trades[date], y=trades[price], name=label, mode="markers", marker=dict(size=11, color=color, symbol="circle", line=dict(color="white", width=1))))
    fig.update_layout(height=540, yaxis_title="Adjusted price (USD)", xaxis_title="Date", hovermode="x unified", legend=dict(orientation="h", y=1.1), margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)
    st.info("Buy dots mark a new 50-day / 200-day crossover. Sell dots mark the first close at least 15% above entry, or the last available close within 60 calendar days.")
elif page == "Trade statistics":
    if trades.empty:
        st.info("No golden cross trades were detected in this period.")
    else:
        profits = trades.ProfitPct
        wins = int((profits > 0).sum())
        a, b, c, d = st.columns(4)
        a.metric("Total trades", len(trades))
        b.metric("Win rate", f"{wins / len(trades):.1%}")
        c.metric("Average trade return", f"{profits.mean():.2f}%")
        d.metric("Average holding period", f"{trades.HoldingDays.mean():.1f} days")
        summary = {
            "Winning trades": wins,
            "Losing trades": int((profits < 0).sum()),
            "Break-even trades": int((profits == 0).sum()),
            "Best trade (%)": round(profits.max(), 2),
            "Worst trade (%)": round(profits.min(), 2),
            "Target reached": int((trades.SellReason == "Target reached").sum()),
            "Holding-period / data-end exits": int((trades.SellReason == "Max holding period").sum()),
        }
        st.dataframe(pd.DataFrame(summary.items(), columns=["Statistic", "Value"]), hide_index=True, use_container_width=True)
        st.caption("Average trade return is an arithmetic average across trades, not a cumulative portfolio return.")
else:
    if trades.empty:
        st.info("No trades to display.")
    else:
        display = trades.copy()
        for column in ["BuyDate", "SellDate"]:
            display[column] = display[column].dt.strftime("%Y-%m-%d")
        display.index = range(1, len(display) + 1)
        st.dataframe(display, use_container_width=True, column_config={
            "BuyPrice": st.column_config.NumberColumn("Buy price (USD)", format="%.2f"),
            "SellPrice": st.column_config.NumberColumn("Sell price (USD)", format="%.2f"),
            "ProfitPct": st.column_config.NumberColumn("Trade return (%)", format="%.2f"),
        })
        st.download_button("Download trade records", display.to_csv(index_label="Trade"), "MSFT_trades.csv", "text/csv")

with st.expander("How the lab strategy works and its assumptions"):
    st.markdown("""
**Backtesting** applies a rule to historical prices to inspect hypothetical trades.
**Golden cross** means today's 50-day average exceeds the 200-day average while
the previous observation's 50-day average was at or below the 200-day average.

The notebook assumes entry at the same closing price used to detect the signal,
omits fees and slippage, and evaluates each crossover independently, so trades
can overlap. It uses adjusted prices and the first 200 observations as warm-up.
If history ends before a full 60-day holding window, it exits at the last available
close and still labels it “Max holding period.” These conventions are preserved
to match the lab. They are a simplified demonstration, not an executable trading system.
""")
