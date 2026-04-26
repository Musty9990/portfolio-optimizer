# 📊 Portfolio Optimizer — Modern Portfolio Theory Tool

> An interactive web application that finds the optimal asset allocation for any portfolio using the Nobel Prize-winning Markowitz Modern Portfolio Theory. Supports US stocks and BIST (Borsa İstanbul) equities — with full Excel export.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)


## 🌐 Live Demo

**Try it now:** https://turkish-portfolio-optimizer.streamlit.app/

No installation needed — pick a preset (US Tech / BIST Banks / Custom), hit Optimize, and explore the interactive charts.


## 🌐 Live Demo

**Try it now:** https://turkish-portfolio-optimizer.streamlit.app/

No installation needed — pick a preset (US Tech / BIST Banks / Custom), hit Optimize Portfolio, and explore the interactive charts.

---



## 💡 What It Does

Given any list of stock tickers, this tool:

1. 📥 Fetches 2+ years of historical prices via Yahoo Finance
2. 📐 Computes expected returns and covariance matrix (Markowitz inputs)
3. ⭐ Finds the Max Sharpe Portfolio — best risk-adjusted return
4. 🛡️ Finds the Min Volatility Portfolio — lowest possible risk
5. 📈 Plots the Efficient Frontier — set of all rationally-optimal portfolios
6. 💾 Exports a multi-sheet professional Excel report

All in an interactive dark-mode web UI built with Streamlit.

---

## 🌐 Tested Use Cases

### 🇹🇷 BIST Banks Portfolio
Optimize a basket of Turkish banks (GARAN, AKBNK, ISCTR, YKBNK):
- Max Sharpe: ~37% expected return, Sharpe 0.89
- Min Volatility: ~22% return with reduced risk

### 🇺🇸 US Tech Diversification
AAPL, MSFT, GOOGL, AMZN, NVDA over 2 years:
- Max Sharpe portfolio concentrates in NVDA + GOOGL
- Min Vol prefers MSFT + AAPL stability

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| UI            | Streamlit |
| Optimization  | PyPortfolioOpt |
| Data          | yfinance |
| Visualization | Plotly |
| Data Wrangling| pandas, numpy |
| Reports       | openpyxl |

---

## 🧱 Architecture

The project follows a modular structure:

- app.py — Streamlit web UI (entry point)
- core/data_fetcher.py — yfinance wrapper with error handling
- core/optimizer.py — Markowitz solver using PyPortfolioOpt
- core/visualizer.py — Plotly interactive charts
- utils/exporters.py — Multi-sheet Excel report generation
- requirements.txt, README.md, LICENSE

Each module has a single responsibility and can be tested or reused independently. The optimizer module runs standalone via "python -m core.optimizer" for quick smoke-testing without launching the UI.

---

## 🚀 Installation

Clone the repo, create a virtual environment, install dependencies:

    git clone https://github.com/Musty9990/portfolio-optimizer.git
    cd portfolio-optimizer
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

---

## 📖 Usage

Web App (Recommended):

    streamlit run app.py

Opens at http://localhost:8501. Pick a preset, hit Optimize Portfolio, explore the charts.

Programmatic Use:

    from core.data_fetcher import fetch_price_data
    from core.optimizer import optimize_max_sharpe
    prices = fetch_price_data(["AAPL", "MSFT", "GOOGL"], period="2y")
    result = optimize_max_sharpe(prices, risk_free_rate=0.02)
    print(result)

---

## 📑 Excel Report Format

The downloaded .xlsx contains 5 sheets:

| Sheet | Content |
|-------|---------|
| Summary    | Period, assets, key metrics for both portfolios |
| Max Sharpe | Detailed weights for the Max Sharpe portfolio |
| Min Vol    | Detailed weights for the Min Volatility portfolio |
| Prices     | Full historical price history |
| Frontier   | All efficient frontier data points |

---

## 🎯 Why This Project

This tool was built to demonstrate:

- Quantitative finance fundamentals — Markowitz MPT, Sharpe ratio, efficient frontier
- Production-grade Python engineering — modular code, type hints, structured logging, error handling
- End-to-end product thinking — from data ingestion to interactive UI to exportable reports
- Cross-market support — works for both US and Turkish (BIST) equities out of the box

---

## 🗺️ Roadmap

- Black-Litterman model for incorporating investor views
- Risk parity optimization
- Multi-currency support (TL, USD, EUR)
- Backtesting module (rolling rebalancing simulation)
- Deploy live demo to Streamlit Community Cloud

---

## 📄 License

MIT License — see LICENSE file.

---

## 👤 Author

Mustafa — Electrical Engineering student building Python automation and quantitative finance tools.

GitHub: https://github.com/Musty9990
