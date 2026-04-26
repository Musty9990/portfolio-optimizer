"""
Portfolio Optimizer Module
==========================
Implements Modern Portfolio Theory (Markowitz) using PyPortfolioOpt.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, expected_returns, risk_models
from pypfopt.objective_functions import L2_reg

log = logging.getLogger(__name__)


@dataclass
class PortfolioResult:
    """Holds the result of a single portfolio optimization."""
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float

    def __str__(self) -> str:
        weights_str = "\n".join(
            f"  {ticker:12s} {w*100:6.2f}%"
            for ticker, w in sorted(self.weights.items(), key=lambda x: -x[1])
            if w > 0.001
        )
        return (
            f"📊 Portfolio Allocation:\n{weights_str}\n"
            f"📈 Expected Annual Return: {self.expected_return*100:.2f}%\n"
            f"📉 Annual Volatility:      {self.volatility*100:.2f}%\n"
            f"⭐ Sharpe Ratio:           {self.sharpe_ratio:.3f}"
        )


def calculate_inputs(
    prices: pd.DataFrame,
    frequency: int = 252,
) -> Tuple[pd.Series, pd.DataFrame]:
    """Compute expected returns and covariance matrix from prices."""
    mu = expected_returns.mean_historical_return(prices, frequency=frequency)
    sigma = risk_models.sample_cov(prices, frequency=frequency)
    log.info(f"📐 Computed inputs for {len(mu)} assets.")
    return mu, sigma


def optimize_max_sharpe(
    prices: pd.DataFrame,
    risk_free_rate: float = 0.02,
    weight_bounds: Tuple[float, float] = (0, 1),
) -> PortfolioResult:
    """Find the portfolio that maximizes the Sharpe ratio."""
    mu, sigma = calculate_inputs(prices)

    ef = EfficientFrontier(mu, sigma, weight_bounds=weight_bounds)
    ef.max_sharpe(risk_free_rate=risk_free_rate)

    weights = ef.clean_weights()
    perf = ef.portfolio_performance(risk_free_rate=risk_free_rate)

    return PortfolioResult(
        weights=dict(weights),
        expected_return=perf[0],
        volatility=perf[1],
        sharpe_ratio=perf[2],
    )


def optimize_min_volatility(
    prices: pd.DataFrame,
    weight_bounds: Tuple[float, float] = (0, 1),
) -> PortfolioResult:
    """Find the portfolio with the minimum volatility."""
    mu, sigma = calculate_inputs(prices)

    ef = EfficientFrontier(mu, sigma, weight_bounds=weight_bounds)
    ef.min_volatility()

    weights = ef.clean_weights()
    perf = ef.portfolio_performance()

    return PortfolioResult(
        weights=dict(weights),
        expected_return=perf[0],
        volatility=perf[1],
        sharpe_ratio=perf[2],
    )


def generate_efficient_frontier(
    prices: pd.DataFrame,
    n_points: int = 30,
    weight_bounds: Tuple[float, float] = (0, 1),
) -> pd.DataFrame:
    """
    Generate (return, volatility) points along the efficient frontier.

    Uses min-vol portfolio's return as the lower bound and the highest individual
    asset return as the upper bound, scanning n_points target returns between.
    """
    mu, sigma = calculate_inputs(prices)

    # Lower bound: min volatility portfolio's expected return
    ef_minvol = EfficientFrontier(mu, sigma, weight_bounds=weight_bounds)
    ef_minvol.min_volatility()
    min_ret = ef_minvol.portfolio_performance()[0]

    # Upper bound: highest single-asset return (slightly below to stay feasible)
    max_ret = mu.max() * 0.999

    if max_ret <= min_ret:
        log.warning("Max return ≤ min volatility return — frontier collapsed.")
        return pd.DataFrame(columns=["return", "volatility"])

    target_returns = np.linspace(min_ret, max_ret, n_points)
    frontier = []

    for target in target_returns:
        try:
            ef = EfficientFrontier(mu, sigma, weight_bounds=weight_bounds)
            ef.efficient_return(target_return=target)
            ret, vol, _ = ef.portfolio_performance()
            frontier.append({"return": ret, "volatility": vol})
        except Exception:
            continue

    df = pd.DataFrame(frontier).drop_duplicates().reset_index(drop=True)
    log.info(f"📈 Generated {len(df)} efficient frontier points.")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    from core.data_fetcher import fetch_price_data

    test_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
    prices = fetch_price_data(test_tickers, period="2y")

    print("\n=== MAX SHARPE PORTFOLIO ===")
    print(optimize_max_sharpe(prices))

    print("\n=== MIN VOLATILITY PORTFOLIO ===")
    print(optimize_min_volatility(prices))

    print("\n=== EFFICIENT FRONTIER ===")
    frontier = generate_efficient_frontier(prices, n_points=20)
    print(frontier)
