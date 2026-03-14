"""
DATA COLLECTOR MODULE
Fetches live market data from yfinance for all tracked instruments.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataCollector:
    """Handles all market data acquisition from yfinance."""

    # ── Instrument Registry ─────────────────────────────────────────────────
    INSTRUMENTS = {
        "CL=F":      "Crude Oil (WTI)",
        "GC=F":      "Gold",
        "HG=F":      "Copper",
        "^GSPC":     "S&P 500",
        "^VIX":      "VIX Volatility Index",
        "DX-Y.NYB":  "US Dollar Index",
        "^TNX":      "10Y Treasury Yield",
        "^DJI":      "Dow Jones Industrial",
        "^IXIC":     "NASDAQ Composite",
    }

    def __init__(self, period: str = "3mo", interval: str = "1d"):
        self.period = period
        self.interval = interval
        self.data: dict[str, pd.DataFrame] = {}

    def fetch_ticker(self, ticker: str) -> pd.DataFrame:
        """Fetch OHLCV data for a single ticker."""
        try:
            t = yf.Ticker(ticker)
            df = t.history(period=self.period, interval=self.interval)

            if df.empty:
                return pd.DataFrame()

            # Standardize columns
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df.index = pd.to_datetime(df.index)
            df.index = df.index.tz_localize(None)  # Remove timezone
            df.dropna(subset=['Close'], inplace=True)
            return df

        except Exception as e:
            print(f"[DataCollector] Error fetching {ticker}: {e}")
            return pd.DataFrame()

    def fetch_all(self) -> dict[str, pd.DataFrame]:
        """Fetch data for all instruments."""
        results = {}
        for ticker in self.INSTRUMENTS:
            df = self.fetch_ticker(ticker)
            if not df.empty:
                results[ticker] = df

        # If critical data missing, generate synthetic fallback
        results = self._fill_synthetic_fallbacks(results)
        self.data = results
        return results

    def _fill_synthetic_fallbacks(self, data: dict) -> dict:
        """Generate synthetic data for any failed fetches."""
        defaults = {
            "CL=F":     (75.0, 2.0),
            "GC=F":     (2050.0, 30.0),
            "HG=F":     (4.0, 0.1),
            "^GSPC":    (5200.0, 80.0),
            "^VIX":     (18.0, 2.0),
            "DX-Y.NYB": (104.0, 1.0),
            "^TNX":     (4.5, 0.1),
        }

        dates = pd.date_range(end=datetime.now(), periods=90, freq='B')

        for ticker, (base, vol) in defaults.items():
            if ticker not in data or data[ticker].empty:
                np.random.seed(hash(ticker) % 2**31)
                prices = base + np.cumsum(np.random.randn(len(dates)) * vol)
                prices = np.abs(prices)
                data[ticker] = pd.DataFrame({
                    'Open':   prices * 0.998,
                    'High':   prices * 1.005,
                    'Low':    prices * 0.995,
                    'Close':  prices,
                    'Volume': np.random.randint(1_000_000, 10_000_000, len(dates)).astype(float)
                }, index=dates)

        return data

    def get_latest_price(self, ticker: str) -> float:
        """Get the most recent closing price for a ticker."""
        if ticker in self.data and not self.data[ticker].empty:
            return float(self.data[ticker]['Close'].iloc[-1])
        return 0.0

    def get_pct_change(self, ticker: str, periods: int = 1) -> float:
        """Get percentage change over N periods."""
        if ticker in self.data and len(self.data[ticker]) > periods:
            series = self.data[ticker]['Close']
            return float((series.iloc[-1] / series.iloc[-1 - periods] - 1) * 100)
        return 0.0
