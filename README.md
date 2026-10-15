# COMP4145 Lab 2 Single Stock Trading App

Implements Parts A–C preparation of the supplied lab. Stops before the Project Development 2 briefing. The original calculator in the parent folder is separate.

## Run locally on macOS

```bash
cd /Users/jackytam/Code_Practice/COMP4145_lab2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python trading_strategy.py
python -m streamlit run app.py
```

Open http://localhost:8501. Keep the terminal running; Ctrl+C stops it.

## Three pages

1. Price chart: all downloaded prices, MA50, MA200, green buy dots and red sell dots.
2. Trade statistics: trade count, win rate, average return and holding period, winners/losers and exit reasons.
3. Detailed trades: entry/exit dates and prices, holding days, returns, reasons and CSV export.

## Answers to the lab questions

The code downloads five years of Microsoft (MSFT) daily prices from Yahoo Finance, calculates two moving averages, identifies golden crosses, simulates trades and summarizes results. Backtesting means applying rules to historical data to inspect hypothetical results. A golden cross is a short moving average crossing above a long moving average.

The buy signal is:

```python
data['GoldenCross'] = (
    (data['MA50'] > data['MA200'])
    & (data['MA50'].shift(1) <= data['MA200'].shift(1))
)
```

Both conditions must be true: MA50 is above MA200 today, and was at or below it on the previous observation. It does not buy on every day MA50 is higher. The script assumes buying at that day's close.

Sell at the first close at least 1.15 times the buy price within 60 calendar days. Otherwise use the last observed close on or before that deadline. When history ends early, the original notebook also uses the last close and labels it Max holding period. Weekends mean the elapsed holding period can be less than 60 days.

## Fidelity and limitations

`notebook_original.py` preserves the supplied Part II code. `trading_strategy.py` adds an import-safe main guard, explicit adjusted pricing, empty-data handling and stable empty trade columns. Trading rules remain unchanged. The UI separates break-even trades from losses; the original console summary counts break-even trades as losses.

The first 200 observations are warm-up. Same-close signal/execution is a simplifying assumption; trades may overlap and omit fees/slippage. Average trade return is not a portfolio return. Prices are adjusted and recent windows/results change when rerun. This is a historical lab demonstration, not a brokerage integration.

## Copilot access methods in the handout

- Editor Inline Chat: asks about or edits code in the active editor (handout Windows shortcut Ctrl+I).
- Chat Window: ongoing conversation and agent workflow (Ctrl+Shift+I).
- Quick Chat: brief questions without the full side-panel conversation (Ctrl+Shift+Alt+I).

This implementation was completed in Codex on macOS; the handout's Windows default-browser and Copilot model-selection steps do not apply to this execution environment.

## GitHub and Streamlit Community Cloud

Publish only this project folder to `COMP4145_lab2`, not the parent workspace. Exclude `.venv`, secrets and local artifacts with `.gitignore`.

On Streamlit Community Cloud select the repository, branch `main`, and entry point `app.py`. Select Python 3.11 in advanced settings. Dependencies are supplied by `requirements.txt`. See https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app.

Source notebook: https://colab.research.google.com/drive/1G_vS2pADjCSbezG0tFyIhr-8ksWnx-Wh?usp=sharing (Part II only).
