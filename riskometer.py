"""
RISKOMETER MODEL
Computes the composite market risk score using a weighted 5-factor model.
"""

import pandas as pd
import numpy as np
from typing import Any


class RiskometerModel:
    """
    Computes market risk on a 0–10 scale using:
      0.30 × MacroScore
      0.20 × SentimentScore
      0.20 × TechnicalScore
      0.15 × OrderFlowScore
      0.15 × RiskMetricsScore
    """

    WEIGHTS = {
        'macro':        0.30,
        'sentiment':    0.20,
        'technical':    0.20,
        'order_flow':   0.15,
        'risk_metrics': 0.15,
    }

    def __init__(self, indicators: dict, raw_data: dict):
        self.ind = indicators
        self.raw = raw_data

    # ════════════════════════════════════════════════════════════════════════
    # MAIN COMPUTE
    # ════════════════════════════════════════════════════════════════════════

    def compute(self) -> dict[str, Any]:
        """Run the full riskometer calculation."""
        scores = {
            'macro':        self._score_macro(),
            'sentiment':    self._score_sentiment(),
            'technical':    self._score_technical(),
            'order_flow':   self._score_order_flow(),
            'risk_metrics': self._score_risk_metrics(),
        }

        # Weighted composite
        composite = sum(scores[k] * self.WEIGHTS[k] for k in scores)
        risk_score = round(composite * 10, 2)  # Scale to 0-10

        market_mode = self._determine_mode(risk_score, scores)

        return {
            'risk_score':       risk_score,
            'composite_raw':    composite,
            'market_mode':      market_mode,
            'component_scores': scores,
            'all_indicators':   self._flatten_indicators(),
        }

    # ════════════════════════════════════════════════════════════════════════
    # COMPONENT SCORERS (all return 0–1, higher = more risk)
    # ════════════════════════════════════════════════════════════════════════

    def _score_macro(self) -> float:
        macro = self.ind.get('macro', {})
        signals = []

        # Bond yield: high yield = risk (above 4% is risk-off pressure)
        bond = macro.get('bond_yield', 4.0)
        signals.append(self._norm(bond, 1.0, 6.0))

        # VIX component from macro context
        vix = self.ind.get('sentiment', {}).get('vix', 20)
        signals.append(self._norm(vix, 10, 50))

        # Dollar index: very high = risk-off for EM
        dxy = macro.get('dollar_index', 104)
        signals.append(self._norm(dxy, 88, 115))

        # Oil price: very high = stagflationary risk
        oil = macro.get('oil_price', 75)
        signals.append(self._norm(oil, 30, 130))

        # Gold: rising gold = fear
        gold_chg = macro.get('gold_price_pct_chg', 0)
        gold_signal = 0.5 + gold_chg * 0.05
        signals.append(max(0, min(1, gold_signal)))

        # Copper: falling copper = recession risk (inverted)
        copper_chg = macro.get('copper_price_pct_chg', 0)
        copper_signal = 0.5 - copper_chg * 0.05
        signals.append(max(0, min(1, copper_signal)))

        return float(np.mean(signals))

    def _score_sentiment(self) -> float:
        sent = self.ind.get('sentiment', {})
        signals = []

        # VIX: core fear measure
        vix = sent.get('vix', 20)
        signals.append(self._norm(vix, 10, 50))

        # Put/call ratio
        pcr = sent.get('put_call_ratio', 1.0)
        signals.append(self._norm(pcr, 0.5, 2.0))

        # Fear/greed (inverted — high fear = high risk)
        fg = sent.get('fear_greed_index', 50)
        signals.append(1 - self._norm(fg, 0, 100))

        return float(np.mean(signals))

    def _score_technical(self) -> float:
        # Use S&P 500 as primary
        tech = self.ind.get('technical', {})
        sp_tech = tech.get('^GSPC', tech.get('CL=F', {}))
        signals = []

        if sp_tech:
            # RSI: >70 overbought (complacency risk), <30 oversold (panic)
            rsi = sp_tech.get('rsi', 50)
            # Risk is high at both extremes but differently:
            # High RSI = momentum risk, Low RSI = crash/panic
            rsi_signal = abs(rsi - 50) / 50
            signals.append(rsi_signal)

            # ADX: high ADX = strong trend (could be either direction)
            adx = sp_tech.get('adx', 20)
            signals.append(self._norm(adx, 0, 60))

            # Price vs EMA 200 (distance = risk)
            price = sp_tech.get('current_price', 0)
            ema200 = sp_tech.get('ema_200', price)
            if ema200 > 0:
                distance = abs(price - ema200) / ema200
                signals.append(self._norm(distance, 0, 0.2))

            # Bollinger width: wide bands = high vol = risk
            bb_width = sp_tech.get('bb_width', 0.05)
            signals.append(self._norm(bb_width, 0.01, 0.15))

            # MACD histogram direction
            macd_hist = sp_tech.get('macd_hist', 0)
            macd_signal = 0.5 - np.sign(macd_hist) * 0.15
            signals.append(max(0, min(1, macd_signal)))

        return float(np.mean(signals)) if signals else 0.5

    def _score_order_flow(self) -> float:
        of_data = self.ind.get('order_flow', {})
        sp_of = of_data.get('^GSPC', of_data.get('CL=F', {}))
        signals = []

        if sp_of:
            # OBV: negative = distribution (risk)
            obv = sp_of.get('obv', 0)
            obv_signal = 0.5 - np.sign(obv) * 0.2
            signals.append(max(0, min(1, obv_signal)))

            # CMF: negative = money outflow (risk)
            cmf = sp_of.get('cmf', 0)
            cmf_signal = 0.5 - cmf * 2
            signals.append(max(0, min(1, cmf_signal)))

            # MFI: >80 = overbought risk, <20 = panic
            mfi = sp_of.get('mfi', 50)
            mfi_signal = abs(mfi - 50) / 50
            signals.append(mfi_signal)

        return float(np.mean(signals)) if signals else 0.5

    def _score_risk_metrics(self) -> float:
        """Composite of volatility-based risk metrics."""
        signals = []

        # VIX regime
        vix = self.ind.get('sentiment', {}).get('vix', 20)
        signals.append(self._norm(vix, 10, 50))

        # ATR-based volatility across assets
        tech = self.ind.get('technical', {})
        for ticker in ['^GSPC', 'CL=F', 'GC=F']:
            t = tech.get(ticker, {})
            if t:
                price = t.get('current_price', 1)
                atr = t.get('atr', 0)
                if price > 0 and atr > 0:
                    atr_pct = atr / price
                    signals.append(self._norm(atr_pct, 0.001, 0.04))

        # Bond yield volatility (crude proxy)
        bond = self.ind.get('macro', {}).get('bond_yield', 4)
        bond_risk = self._norm(bond, 1, 6)
        signals.append(bond_risk)

        return float(np.mean(signals)) if signals else 0.5

    # ════════════════════════════════════════════════════════════════════════
    # UTILITIES
    # ════════════════════════════════════════════════════════════════════════

    def _norm(self, value: float, low: float, high: float) -> float:
        """Min-max normalize to [0, 1]."""
        if high == low:
            return 0.5
        return float(max(0.0, min(1.0, (value - low) / (high - low))))

    def _determine_mode(self, risk_score: float, scores: dict) -> str:
        """Classify market into Risk-On / Risk-Off / Neutral."""
        if risk_score >= 6.5:
            return "RISK-OFF"
        elif risk_score >= 4.5:
            return "NEUTRAL"
        else:
            return "RISK-ON"

    def _flatten_indicators(self) -> list[dict]:
        """Flatten all indicators into a table for display."""
        rows = []

        # Macro
        macro = self.ind.get('macro', {})
        macro_items = [
            ("Crude Oil Price", "macro", f"${macro.get('oil_price', 0):.2f}", macro.get('oil_price_pct_chg', 0)),
            ("Gold Price", "macro", f"${macro.get('gold_price', 0):.2f}", macro.get('gold_price_pct_chg', 0)),
            ("Dollar Index", "macro", f"{macro.get('dollar_index', 0):.2f}", macro.get('dollar_index_pct_chg', 0)),
            ("10Y Bond Yield", "macro", f"{macro.get('bond_yield', 0):.2f}%", macro.get('bond_yield_pct_chg', 0)),
            ("S&P 500", "macro", f"{macro.get('sp500', 0):.0f}", macro.get('sp500_pct_chg', 0)),
            ("Copper Price", "macro", f"${macro.get('copper_price', 0):.2f}", macro.get('copper_price_pct_chg', 0)),
            ("Gold/Oil Ratio", "macro", f"{macro.get('gold_oil_ratio', 0):.1f}", 0),
            ("Inflation Proxy", "macro", "2.80%", 0),
            ("GDP Growth Proxy", "macro", "2.10%", 0),
        ]
        for name, cat, val, chg in macro_items:
            rows.append({"Indicator": name, "Category": cat.title(), "Value": val,
                         "Change%": f"{chg:+.2f}%",
                         "Signal": "⬆ RISK" if chg > 0.5 else "⬇ OK" if chg < -0.5 else "➡ NEUTRAL"})

        # Sentiment
        sent = self.ind.get('sentiment', {})
        rows.append({"Indicator": "VIX", "Category": "Sentiment",
                     "Value": f"{sent.get('vix', 0):.2f}",
                     "Change%": "—",
                     "Signal": "⬆ FEAR" if sent.get('vix', 20) > 25 else "➡ NEUTRAL"})
        rows.append({"Indicator": "Put/Call Ratio", "Category": "Sentiment",
                     "Value": f"{sent.get('put_call_ratio', 1):.2f}",
                     "Change%": "—",
                     "Signal": "⬆ BEARISH" if sent.get('put_call_ratio', 1) > 1.2 else "➡ NEUTRAL"})
        rows.append({"Indicator": "Fear & Greed Index", "Category": "Sentiment",
                     "Value": f"{sent.get('fear_greed_index', 50):.0f}/100",
                     "Change%": "—",
                     "Signal": "⬆ FEAR" if sent.get('fear_greed_index', 50) < 30 else "➡ NEUTRAL"})

        # Technical (S&P 500)
        tech = self.ind.get('technical', {}).get('^GSPC', {})
        tech_items = [
            ("RSI (14)", f"{tech.get('rsi', 0):.1f}"),
            ("MACD", f"{tech.get('macd', 0):.2f}"),
            ("MACD Signal", f"{tech.get('macd_signal', 0):.2f}"),
            ("ADX", f"{tech.get('adx', 0):.1f}"),
            ("ATR", f"{tech.get('atr', 0):.2f}"),
            ("VWAP", f"${tech.get('vwap', 0):.2f}"),
            ("EMA 50", f"${tech.get('ema_50', 0):.2f}"),
            ("EMA 200", f"${tech.get('ema_200', 0):.2f}"),
            ("Bollinger Width", f"{tech.get('bb_width', 0):.4f}"),
            ("Stochastic %K", f"{tech.get('stoch_k', 0):.1f}"),
        ]
        for name, val in tech_items:
            rows.append({"Indicator": name, "Category": "Technical",
                         "Value": val, "Change%": "—", "Signal": "—"})

        # Order Flow
        of = self.ind.get('order_flow', {}).get('^GSPC', {})
        obv = of.get('obv', 0)
        cmf = of.get('cmf', 0)
        mfi = of.get('mfi', 50)
        rows.append({"Indicator": "OBV", "Category": "Order Flow",
                     "Value": f"{obv/1e6:.1f}M" if abs(obv) > 1e6 else f"{obv:.0f}",
                     "Change%": "—",
                     "Signal": "⬆ BUYING" if obv > 0 else "⬇ SELLING"})
        rows.append({"Indicator": "CMF", "Category": "Order Flow",
                     "Value": f"{cmf:.4f}", "Change%": "—",
                     "Signal": "⬆ INFLOW" if cmf > 0 else "⬇ OUTFLOW"})
        rows.append({"Indicator": "MFI", "Category": "Order Flow",
                     "Value": f"{mfi:.1f}", "Change%": "—",
                     "Signal": "⬆ OVERBOUGHT" if mfi > 80 else "⬇ OVERSOLD" if mfi < 20 else "➡ NEUTRAL"})

        return rows

    def display_full_table(self, st) -> None:
        """Render the full indicator table in Streamlit."""
        rows = self._flatten_indicators()
        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Indicator": st.column_config.TextColumn("Indicator", width="medium"),
                "Category": st.column_config.TextColumn("Category", width="small"),
                "Value": st.column_config.TextColumn("Current Value", width="small"),
                "Change%": st.column_config.TextColumn("1D Change", width="small"),
                "Signal": st.column_config.TextColumn("Signal", width="medium"),
            }
        )
