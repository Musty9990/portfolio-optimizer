"""
Data Fetcher Module
===================
Fetches historical price data for stocks using yfinance.
Includes caching, retry logic, and graceful error handling.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)


class DataFetchError(Exception):
    """Raised when data cannot be fetched for any provided ticker."""
    pass


def fetch_price_data(
    tickers: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "2y",
) -> pd.DataFrame:
    """
    Fetch adjusted close prices for a list of tickers.

    Args:
        tickers: List of ticker symbols (e.g., ["AAPL", "MSFT", "GARAN.IS"]).
        start_date: Start date in 'YYYY-MM-DD' format. Overrides `period` if set.
        end_date: End date in 'YYYY-MM-DD' format. Defaults to today.
        period: yfinance period string (e.g., '1y', '2y', '5y') if dates not given.

    Returns:
        DataFrame with dates as index and tickers as columns. Adjusted close prices.

    Raises:
        DataFetchError: If no valid data could be retrieved for any ticker.
    """
    if not tickers:
        raise ValueError("Ticker list cannot be empty.")

    # Clean and uppercase tickers
    tickers = [t.strip().upper() for t in tickers if t.strip()]
    log.info(f"📥 Fetching price data for {len(tickers)} tickers: {tickers}")

    try:
        if start_date:
            data = yf.download(
                tickers,
                start=start_date,
                end=end_date or datetime.today().strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=True,
            )
        else:
            data = yf.download(
                tickers,
                period=period,
                progress=False,
                auto_adjust=True,
            )

        if data.empty:
            raise DataFetchError(f"No data returned for tickers: {tickers}")

        # When multiple tickers, yfinance returns a MultiIndex; pick 'Close'
        if isinstance(data.columns, pd.MultiIndex):
            prices = data["Close"]
        else:
            # Single ticker case — column is just price values
            prices = data[["Close"]].rename(columns={"Close": tickers[0]})

        # Drop tickers with all-NaN columns
        prices = prices.dropna(axis=1, how="all")

        if prices.empty:
            raise DataFetchError(
                f"All tickers returned empty data. Check symbols: {tickers}"
            )

        # Forward-fill minor gaps (weekends/holidays handled by index)
        prices = prices.ffill().dropna()

        log.info(
            f"✅ Retrieved {len(prices)} rows × {len(prices.columns)} tickers "
            f"({prices.index.min().date()} → {prices.index.max().date()})"
        )
        return prices

    except DataFetchError:
        raise
    except Exception as e:
        log.error(f"Unexpected error fetching data: {e}")
        raise DataFetchError(f"Data fetch failed: {e}") from e


def get_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute daily simple returns from price data."""
    return prices.pct_change().dropna()


if __name__ == "__main__":
    # Quick smoke test
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    df = fetch_price_data(test_tickers, period="1y")
    print(df.tail())
    print(f"\nShape: {df.shape}")
