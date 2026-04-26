"""
Visualizer Module
=================
Plotly-based interactive charts for portfolio analysis.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.optimizer import PortfolioResult


def plot_efficient_frontier(
    frontier: pd.DataFrame,
    max_sharpe: PortfolioResult,
    min_vol: PortfolioResult,
) -> go.Figure:
    """
    Plot the efficient frontier with Max Sharpe and Min Vol portfolios marked.
    """
    fig = go.Figure()

    # Frontier curve
    fig.add_trace(go.Scatter(
        x=frontier["volatility"] * 100,
        y=frontier["return"] * 100,
        mode="lines+markers",
        name="Efficient Frontier",
        line=dict(color="#1f77b4", width=3),
        marker=dict(size=6),
        hovertemplate="Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>",
    ))

    # Max Sharpe point
    fig.add_trace(go.Scatter(
        x=[max_sharpe.volatility * 100],
        y=[max_sharpe.expected_return * 100],
        mode="markers",
        name=f"Max Sharpe (SR={max_sharpe.sharpe_ratio:.2f})",
        marker=dict(size=18, color="gold", symbol="star",
                    line=dict(color="black", width=2)),
        hovertemplate=(
            f"<b>Max Sharpe Portfolio</b><br>"
            f"Volatility: {max_sharpe.volatility*100:.2f}%<br>"
            f"Return: {max_sharpe.expected_return*100:.2f}%<br>"
            f"Sharpe: {max_sharpe.sharpe_ratio:.3f}<extra></extra>"
        ),
    ))

    # Min Vol point
    fig.add_trace(go.Scatter(
        x=[min_vol.volatility * 100],
        y=[min_vol.expected_return * 100],
        mode="markers",
        name=f"Min Volatility (SR={min_vol.sharpe_ratio:.2f})",
        marker=dict(size=16, color="#2ca02c", symbol="diamond",
                    line=dict(color="black", width=2)),
        hovertemplate=(
            f"<b>Min Volatility Portfolio</b><br>"
            f"Volatility: {min_vol.volatility*100:.2f}%<br>"
            f"Return: {min_vol.expected_return*100:.2f}%<extra></extra>"
        ),
    ))

    fig.update_layout(
        title="Efficient Frontier — Risk vs Return",
        xaxis_title="Annual Volatility (Risk) %",
        yaxis_title="Annual Expected Return %",
        template="plotly_white",
        height=550,
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_allocation_pie(result: PortfolioResult, title: str = "Portfolio Allocation") -> go.Figure:
    """Pie chart of portfolio weights (filtering out near-zero allocations)."""
    weights = {k: v for k, v in result.weights.items() if v > 0.001}

    fig = px.pie(
        names=list(weights.keys()),
        values=list(weights.values()),
        title=title,
        hole=0.4,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Weight: %{percent}<extra></extra>",
    )
    fig.update_layout(template="plotly_white", height=450)
    return fig


def plot_price_history(prices: pd.DataFrame) -> go.Figure:
    """Normalized price history chart (all tickers start at 100)."""
    normalized = prices / prices.iloc[0] * 100

    fig = go.Figure()
    for col in normalized.columns:
        fig.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized[col],
            mode="lines",
            name=col,
            hovertemplate=f"<b>{col}</b><br>Date: %{{x}}<br>Indexed: %{{y:.2f}}<extra></extra>",
        ))

    fig.update_layout(
        title="Normalized Price History (Base = 100)",
        xaxis_title="Date",
        yaxis_title="Indexed Price",
        template="plotly_white",
        height=450,
        hovermode="x unified",
    )
    return fig
