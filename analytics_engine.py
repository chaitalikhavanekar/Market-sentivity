"""
ANALYTICS ENGINE
Computes all technical, order-flow, and macro indicators.
"""

import pandas as pd
import numpy as np
from typing import Any


class AnalyticsEngine:
    """
    Computes 30+ market indicators across four categories:
    Technical | Order Flow | Macro | Sentiment
    """

    def __init__(self, raw_data: dict[str, pd.DataFrame]):
        self.raw = raw_data

    # ════════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ════════════════════════════════════════════════════════════════════════

    def compute_all(self) -> dict[str, Any]:
        """Compute all indicator categories."""
        return {
            'technical':  self._compute_technical_all(),
            'order_flow': self._compute_order_flow_all(),
            'macro':      self._compute_macro(),
            'sentiment':  self._compute_sentiment(),
        }

    # ════════════════════════════════════════════════════════════════════════
    # TECHNICAL INDICATORS
    # ════════════════════════════════════════════════════════════════════════

    def _compute_technical_all(self) -> dict:
        result = {}
        for ticker, df in self.raw.items():
            if not df.empty and len(df) >= 20:
                result[ticker] = self._compute_technical(df)
        return result

    def _compute_technical(self, df: pd.DataFrame) -> dict:
        """Compute all technical indicators for a single OHLCV DataFrame."""
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']

        return {
            'rsi':          self._rsi(close, 14),
            'macd':         self._macd(close),
            'macd_signal':  self._macd_signal(close),
            'macd_hist':    self._macd_histogram(close),
            'bb_upper':     self._bollinger_upper(close),
            'bb_lower':     self._bollinger_lower(close),
            'bb_mid':       self._bollinger_mid(close),
            'bb_width':     self._bollinger_width(close),
            'ema_50':       self._ema(close, 50),
            'ema_200':      self._ema(close, 200),
            'ema_20':       self._ema(close, 20),
            'atr':          self._atr(high, low, close, 14),
            'adx':          self._adx(high, low, close, 14),
            'vwap':         self._vwap(high, low, close, volume),
            'roc':          self._roc(close, 10),
            'stoch_k':      self._stochastic_k(high, low, close, 14),
            'current_price': float(close.iloc[-1]),
        }

    # ── RSI ──────────────────────────────────────────────────────────────────
    def _rsi(self, close: pd.Series, period: int = 14) -> float:
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not rsi.empty else 50.0

    # ── MACD ─────────────────────────────────────────────────────────────────
    def _macd_line(self, close: pd.Series) -> pd.Series:
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        return ema12 - ema26

    def _macd(self, close: pd.Series) -> float:
        return float(self._macd_line(close).iloc[-1]) if len(close) > 26 else 0.0

    def _macd_signal(self, close: pd.Series) -> float:
        macd_line = self._macd_line(close)
        signal = macd_line.ewm(span=9, adjust=False).mean()
        return float(signal.iloc[-1]) if not signal.empty else 0.0

    def _macd_histogram(self, close: pd.Series) -> float:
        return self._macd(close) - self._macd_signal(close)

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    def _bollinger_mid(self, close: pd.Series, window: int = 20) -> float:
        return float(close.rolling(window).mean().iloc[-1]) if len(close) >= window else float(close.iloc[-1])

    def _bollinger_upper(self, close: pd.Series, window: int = 20, std: float = 2.0) -> float:
        sma = close.rolling(window).mean()
        sd = close.rolling(window).std()
        return float((sma + std * sd).iloc[-1]) if len(close) >= window else float(close.iloc[-1])

    def _bollinger_lower(self, close: pd.Series, window: int = 20, std: float = 2.0) -> float:
        sma = close.rolling(window).mean()
        sd = close.rolling(window).std()
        return float((sma - std * sd).iloc[-1]) if len(close) >= window else float(close.iloc[-1])

    def _bollinger_width(self, close: pd.Series, window: int = 20) -> float:
        upper = self._bollinger_upper(close, window)
        lower = self._bollinger_lower(close, window)
        mid = self._bollinger_mid(close, window)
        return (upper - lower) / mid if mid > 0 else 0.0

    # ── EMA ──────────────────────────────────────────────────────────────────
    def _ema(self, close: pd.Series, period: int) -> float:
        if len(close) < period:
            return float(close.iloc[-1])
        return float(close.ewm(span=period, adjust=False).mean().iloc[-1])

    # ── ATR ──────────────────────────────────────────────────────────────────
    def _atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.ewm(span=period, adjust=False).mean()
        return float(atr.iloc[-1]) if not atr.empty else 0.0

    # ── ADX ──────────────────────────────────────────────────────────────────
    def _adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        dm_plus = high.diff()
        dm_minus = -low.diff()
        dm_plus = dm_plus.where((dm_plus > dm_minus) & (dm_plus > 0), 0.0)
        dm_minus = dm_minus.where((dm_minus > dm_plus) & (dm_minus > 0), 0.0)

        atr = tr.ewm(span=period, adjust=False).mean()
        di_plus = 100 * dm_plus.ewm(span=period, adjust=False).mean() / atr.replace(0, np.nan)
        di_minus = 100 * dm_minus.ewm(span=period, adjust=False).mean() / atr.replace(0, np.nan)

        dx = 100 * (di_plus - di_minus).abs() / (di_plus + di_minus).replace(0, np.nan)
        adx = dx.ewm(span=period, adjust=False).mean()
        return float(adx.iloc[-1]) if not adx.empty and not np.isnan(adx.iloc[-1]) else 20.0

    # ── VWAP ─────────────────────────────────────────────────────────────────
    def _vwap(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> float:
        typical = (high + low + close) / 3
        cum_vol = volume.cumsum()
        vwap = (typical * volume).cumsum() / cum_vol.replace(0, np.nan)
        return float(vwap.iloc[-1]) if not vwap.empty else float(close.iloc[-1])

    # ── ROC ──────────────────────────────────────────────────────────────────
    def _roc(self, close: pd.Series, period: int = 10) -> float:
        if len(close) > period:
            return float((close.iloc[-1] / close.iloc[-1 - period] - 1) * 100)
        return 0.0

    # ── Stochastic ───────────────────────────────────────────────────────────
    def _stochastic_k(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        if len(close) < period:
            return 50.0
        lowest_low = low.rolling(period).min()
        highest_high = high.rolling(period).max()
        k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
        return float(k.iloc[-1]) if not k.empty and not np.isnan(k.iloc[-1]) else 50.0

    # ════════════════════════════════════════════════════════════════════════
    # ORDER FLOW INDICATORS
    # ════════════════════════════════════════════════════════════════════════

    def _compute_order_flow_all(self) -> dict:
        result = {}
        for ticker, df in self.raw.items():
            if not df.empty and len(df) >= 10:
                result[ticker] = self._compute_order_flow(df)
        return result

    def _compute_order_flow(self, df: pd.DataFrame) -> dict:
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']

        return {
            'obv':  self._obv(close, volume),
            'cmf':  self._cmf(high, low, close, volume),
            'mfi':  self._mfi(high, low, close, volume),
        }

    # ── OBV ──────────────────────────────────────────────────────────────────
    def _obv(self, close: pd.Series, volume: pd.Series) -> float:
        direction = close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        obv = (volume * direction).cumsum()
        return float(obv.iloc[-1]) if not obv.empty else 0.0

    # ── CMF ──────────────────────────────────────────────────────────────────
    def _cmf(self, high: pd.Series, low: pd.Series, close: pd.Series,
              volume: pd.Series, period: int = 20) -> float:
        mf_mult = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
        mf_vol = mf_mult * volume
        cmf = mf_vol.rolling(period).sum() / volume.rolling(period).sum().replace(0, np.nan)
        val = float(cmf.iloc[-1])
        return val if not np.isnan(val) else 0.0

    # ── MFI ──────────────────────────────────────────────────────────────────
    def _mfi(self, high: pd.Series, low: pd.Series, close: pd.Series,
              volume: pd.Series, period: int = 14) -> float:
        typical = (high + low + close) / 3
        raw_mf = typical * volume
        pos_mf = raw_mf.where(typical > typical.shift(1), 0.0)
        neg_mf = raw_mf.where(typical < typical.shift(1), 0.0)

        pos_sum = pos_mf.rolling(period).sum()
        neg_sum = neg_mf.rolling(period).sum()
        mr = pos_sum / neg_sum.replace(0, np.nan)
        mfi = 100 - (100 / (1 + mr))
        val = float(mfi.iloc[-1])
        return val if not np.isnan(val) else 50.0

    # ════════════════════════════════════════════════════════════════════════
    # MACRO INDICATORS
    # ════════════════════════════════════════════════════════════════════════

    def _compute_macro(self) -> dict:
        def safe_last(ticker):
            df = self.raw.get(ticker, pd.DataFrame())
            return float(df['Close'].iloc[-1]) if not df.empty else 0.0

        def safe_pct(ticker):
            df = self.raw.get(ticker, pd.DataFrame())
            if not df.empty and len(df) > 1:
                return float((df['Close'].iloc[-1] / df['Close'].iloc[-2] - 1) * 100)
            return 0.0

        oil = safe_last("CL=F")
        gold = safe_last("GC=F")
        copper = safe_last("HG=F")
        dollar = safe_last("DX-Y.NYB")
        bond_yield = safe_last("^TNX")
        sp500 = safe_last("^GSPC")

        # Derived macro signals
        gold_oil_ratio = gold / oil if oil > 0 else 27.0
        real_rate_proxy = bond_yield - 2.5  # Simplified real rate
        risk_appetite = (sp500 / 5000) * 100  # Normalized to 100

        return {
            'oil_price':        oil,
            'oil_price_pct_chg': safe_pct("CL=F"),
            'gold_price':       gold,
            'gold_price_pct_chg': safe_pct("GC=F"),
            'copper_price':     copper,
            'copper_price_pct_chg': safe_pct("HG=F"),
            'dollar_index':     dollar,
            'dollar_index_pct_chg': safe_pct("DX-Y.NYB"),
            'bond_yield':       bond_yield,
            'bond_yield_pct_chg': safe_pct("^TNX"),
            'sp500':            sp500,
            'sp500_pct_chg':    safe_pct("^GSPC"),
            'gold_oil_ratio':   gold_oil_ratio,
            'real_rate_proxy':  real_rate_proxy,
            'risk_appetite':    risk_appetite,
            'inflation_proxy':  2.8,   # Placeholder
            'gdp_growth':       2.1,   # Placeholder
        }

    # ════════════════════════════════════════════════════════════════════════
    # SENTIMENT INDICATORS
    # ════════════════════════════════════════════════════════════════════════

    def _compute_sentiment(self) -> dict:
        vix_df = self.raw.get("^VIX", pd.DataFrame())
        vix = float(vix_df['Close'].iloc[-1]) if not vix_df.empty else 20.0
        vix_5d_avg = float(vix_df['Close'].iloc[-5:].mean()) if not vix_df.empty else vix

        # VIX term structure (approximate)
        vix_contango = (vix_5d_avg - vix) / vix * 100 if vix > 0 else 0

        # Derived sentiment metrics
        put_call_ratio = self._estimate_put_call(vix)
        fear_greed = self._compute_fear_greed(vix)

        return {
            'vix':              vix,
            'vix_5d_avg':       vix_5d_avg,
            'vix_contango':     vix_contango,
            'put_call_ratio':   put_call_ratio,
            'fear_greed_index': fear_greed,
        }

    def _estimate_put_call(self, vix: float) -> float:
        """Estimate put/call ratio from VIX level."""
        base = 0.8 + (vix - 15) * 0.015
        return round(max(0.5, min(2.0, base)), 2)

    def _compute_fear_greed(self, vix: float) -> float:
        """Map VIX to 0-100 fear/greed scale."""
        # VIX 10 = extreme greed (100), VIX 45+ = extreme fear (0)
        raw = 100 - (vix - 10) / 35 * 100
        return max(0, min(100, raw))
