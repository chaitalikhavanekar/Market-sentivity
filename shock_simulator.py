"""
SHOCK SIMULATOR
Applies macroeconomic shock scenarios to market data and indicators.
"""

import pandas as pd
import numpy as np
import copy
from typing import Any


class ShockSimulator:
    """
    Simulates the market impact of major macro shock events.
    Modifies both raw price data and indicator values.
    """

    # ── Shock Definitions ────────────────────────────────────────────────────
    # Each scenario maps indicator → (additive_delta, multiplicative_pct_change)
    SCENARIOS: dict[str, dict] = {

        "WAR": {
            "description": "Geopolitical conflict / Military escalation",
            "raw_shocks": {
                "CL=F":    {"pct": +3.0},   # Oil spike
                "GC=F":    {"pct": +2.0},   # Gold safe haven
                "HG=F":    {"pct": -1.5},   # Copper demand fall
                "^GSPC":   {"pct": -2.5},   # Equities sell-off
                "^VIX":    {"add": +5.0},   # Vol spike
                "DX-Y.NYB":{"pct": +0.8},   # Dollar flight to safety
                "^TNX":    {"add": +0.15},  # Yield spike on inflation
            },
            "indicator_shocks": {
                "macro.oil_price_pct_chg":    +3.0,
                "macro.gold_price_pct_chg":   +2.0,
                "macro.sp500_pct_chg":        -2.5,
                "sentiment.vix":              +5.0,
                "sentiment.put_call_ratio":   +0.3,
                "sentiment.fear_greed_index": -20.0,
            },
        },

        "RATE_HIKE": {
            "description": "Central bank emergency rate hike (+75bps)",
            "raw_shocks": {
                "CL=F":    {"pct": -1.0},
                "GC=F":    {"pct": -1.5},   # Gold falls on higher rates
                "HG=F":    {"pct": -2.0},   # Copper slows
                "^GSPC":   {"pct": -3.0},   # Stocks reprice
                "^VIX":    {"add": +4.0},
                "DX-Y.NYB":{"pct": +1.5},   # Dollar strengthens
                "^TNX":    {"add": +1.0},   # Yield jumps
            },
            "indicator_shocks": {
                "macro.bond_yield":           +1.0,
                "macro.dollar_index_pct_chg": +1.5,
                "macro.sp500_pct_chg":        -3.0,
                "macro.gold_price_pct_chg":   -1.5,
                "sentiment.vix":              +4.0,
                "sentiment.put_call_ratio":   +0.25,
                "sentiment.fear_greed_index": -15.0,
            },
        },

        "OIL_SHOCK": {
            "description": "Major oil supply disruption / OPEC+ cut",
            "raw_shocks": {
                "CL=F":    {"pct": +5.0},   # Oil surges
                "GC=F":    {"pct": +1.0},   # Inflation hedge
                "HG=F":    {"pct": -0.5},
                "^GSPC":   {"pct": -1.5},   # Consumer cost pressure
                "^VIX":    {"add": +3.0},
                "DX-Y.NYB":{"pct": +0.5},
                "^TNX":    {"add": +0.2},   # Inflation expectations
            },
            "indicator_shocks": {
                "macro.oil_price_pct_chg":    +5.0,
                "macro.gold_price_pct_chg":   +1.0,
                "macro.sp500_pct_chg":        -1.5,
                "macro.inflation_proxy":      +0.5,
                "sentiment.vix":              +3.0,
                "sentiment.fear_greed_index": -10.0,
            },
        },

        "PANDEMIC": {
            "description": "Global pandemic / major health crisis",
            "raw_shocks": {
                "CL=F":    {"pct": -8.0},   # Demand collapse
                "GC=F":    {"pct": +3.0},   # Safe haven
                "HG=F":    {"pct": -4.0},   # Industrial demand crash
                "^GSPC":   {"pct": -6.0},   # Market crash
                "^VIX":    {"add": +15.0},  # Massive vol spike
                "DX-Y.NYB":{"pct": +2.0},   # Dollar surge
                "^TNX":    {"add": -0.5},   # Flight to safety
            },
            "indicator_shocks": {
                "macro.oil_price_pct_chg":    -8.0,
                "macro.gold_price_pct_chg":   +3.0,
                "macro.sp500_pct_chg":        -6.0,
                "macro.gdp_growth":           -3.0,
                "sentiment.vix":              +15.0,
                "sentiment.put_call_ratio":   +0.6,
                "sentiment.fear_greed_index": -35.0,
            },
        },

        "CURRENCY_CRISIS": {
            "description": "Emerging market / reserve currency crisis",
            "raw_shocks": {
                "CL=F":    {"pct": -2.0},
                "GC=F":    {"pct": +2.5},   # Dollar alternative
                "HG=F":    {"pct": -2.5},
                "^GSPC":   {"pct": -2.0},
                "^VIX":    {"add": +6.0},
                "DX-Y.NYB":{"pct": +2.5},   # Dollar surges
                "^TNX":    {"add": +0.3},
            },
            "indicator_shocks": {
                "macro.dollar_index_pct_chg": +2.5,
                "macro.gold_price_pct_chg":   +2.5,
                "macro.sp500_pct_chg":        -2.0,
                "sentiment.vix":              +6.0,
                "sentiment.put_call_ratio":   +0.35,
                "sentiment.fear_greed_index": -18.0,
            },
        },
    }

    def __init__(self, raw_data: dict, indicators: dict):
        self.raw = raw_data
        self.indicators = indicators

    # ════════════════════════════════════════════════════════════════════════
    # MAIN APPLY METHOD
    # ════════════════════════════════════════════════════════════════════════

    def apply_shock(
        self,
        scenario_name: str,
        intensity: float = 1.0
    ) -> tuple[dict, dict, dict]:
        """
        Apply a shock scenario to data and indicators.

        Returns:
            shocked_raw:        Modified OHLCV DataFrames
            shocked_indicators: Modified indicator dict
            shock_details:      Summary of applied shocks
        """
        scenario = self.SCENARIOS.get(scenario_name)
        if not scenario:
            return self.raw, self.indicators, {}

        shocked_raw = self._apply_price_shocks(
            scenario['raw_shocks'], intensity
        )
        shocked_indicators, shock_details = self._apply_indicator_shocks(
            scenario['indicator_shocks'], intensity
        )

        return shocked_raw, shocked_indicators, shock_details

    # ════════════════════════════════════════════════════════════════════════
    # PRICE SHOCK APPLICATION
    # ════════════════════════════════════════════════════════════════════════

    def _apply_price_shocks(
        self,
        raw_shocks: dict,
        intensity: float
    ) -> dict[str, pd.DataFrame]:
        """Apply percentage / additive shocks to the last price bar."""
        shocked = {}

        for ticker, df in self.raw.items():
            if df.empty:
                shocked[ticker] = df
                continue

            df_copy = df.copy()
            shock_spec = raw_shocks.get(ticker)

            if shock_spec:
                if 'pct' in shock_spec:
                    multiplier = 1 + (shock_spec['pct'] / 100) * intensity
                    df_copy.loc[df_copy.index[-1], ['Open', 'High', 'Low', 'Close']] *= multiplier
                if 'add' in shock_spec:
                    addend = shock_spec['add'] * intensity
                    df_copy.loc[df_copy.index[-1], ['Open', 'High', 'Low', 'Close']] += addend

            shocked[ticker] = df_copy

        return shocked

    # ════════════════════════════════════════════════════════════════════════
    # INDICATOR SHOCK APPLICATION
    # ════════════════════════════════════════════════════════════════════════

    def _apply_indicator_shocks(
        self,
        indicator_shocks: dict,
        intensity: float
    ) -> tuple[dict, dict]:
        """Apply delta adjustments to computed indicator values."""
        ind = copy.deepcopy(self.indicators)
        applied = {}

        for path, delta in indicator_shocks.items():
            parts = path.split('.')
            scaled_delta = delta * intensity

            # Navigate the indicator dict
            if len(parts) == 2:
                category, key = parts
                if category in ind and isinstance(ind[category], dict):
                    old_val = ind[category].get(key, 0)
                    new_val = old_val + scaled_delta
                    # Clamp VIX and fear/greed to reasonable ranges
                    if 'vix' in key:
                        new_val = max(10, min(80, new_val))
                    if 'fear_greed' in key:
                        new_val = max(0, min(100, new_val))
                    ind[category][key] = new_val
                    applied[key.replace('_', ' ').title()] = scaled_delta

        return ind, applied

    def list_scenarios(self) -> list[dict]:
        """Return scenario metadata for UI display."""
        return [
            {
                "name": name,
                "description": scenario["description"],
                "primary_effect": list(scenario["raw_shocks"].keys())[:3]
            }
            for name, scenario in self.SCENARIOS.items()
        ]
