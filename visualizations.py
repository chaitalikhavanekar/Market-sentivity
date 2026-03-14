"""
VISUALIZATIONS MODULE
All Plotly-based chart renderers for the dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Any


# â”€â”€ Shared Theme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
THEME = {
    "bg":           "#050a0f",
    "bg_card":      "#0d1f35",
    "grid":         "rgba(0,229,255,0.06)",
    "text":         "#e0f4ff",
    "text_muted":   "#5a8aaa",
    "cyan":         "#00e5ff",
    "green":        "#00ff9d",
    "red":          "#ff2d55",
    "orange":       "#ff6b00",
    "yellow":       "#ffd60a",
    "purple":       "#bf5fff",
    "font":         "Share Tech Mono, monospace",
    "font_title":   "Orbitron, monospace",
}

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family=THEME["font"], color=THEME["text"], size=11),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=10, color=THEME["text_muted"]),
        orientation="h", x=0, y=1.02
    ),
)
# margin and showlegend are set per-chart to avoid duplicate-key TypeError


class Visualizer:
    """Factory for all dashboard Plotly visualizations."""

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # RISKOMETER GAUGE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def render_riskometer_gauge(self, risk_result: dict) -> go.Figure:
        score = risk_result.get('risk_score', 5.0)

        # Determine needle color
        if score >= 7:
            gauge_color = THEME["red"]
        elif score >= 5:
            gauge_color = THEME["orange"]
        elif score >= 3:
            gauge_color = THEME["yellow"]
        else:
            gauge_color = THEME["green"]

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            number={
                "font": {"size": 42, "family": THEME["font_title"], "color": gauge_color},
                "suffix": "/10"
            },
            delta={
                "reference": 5.0,
                "font": {"size": 14},
                "increasing": {"color": THEME["red"]},
                "decreasing": {"color": THEME["green"]},
            },
            gauge={
                "axis": {
                    "range": [0, 10],
                    "tickwidth": 1,
                    "tickcolor": THEME["text_muted"],
                    "tickfont": {"size": 10, "family": THEME["font"]},
                    "nticks": 11,
                },
                "bar": {"color": gauge_color, "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 3],   "color": "rgba(0,255,157,0.08)"},
                    {"range": [3, 5],   "color": "rgba(255,214,10,0.08)"},
                    {"range": [5, 7],   "color": "rgba(255,107,0,0.08)"},
                    {"range": [7, 10],  "color": "rgba(255,45,85,0.08)"},
                ],
                "threshold": {
                    "line": {"color": THEME["cyan"], "width": 2},
                    "thickness": 0.75,
                    "value": score,
                },
            },
            title={
                "text": "MARKET RISK SCORE",
                "font": {"size": 11, "family": THEME["font_title"], "color": THEME["text_muted"]},
            },
            domain={"x": [0, 1], "y": [0, 1]},
        ))

        # Add zone annotations
        for x, label, color in [
            (0.08, "LOW", THEME["green"]),
            (0.32, "MODERATE", THEME["yellow"]),
            (0.62, "ELEVATED", THEME["orange"]),
            (0.87, "HIGH", THEME["red"]),
        ]:
            fig.add_annotation(
                x=x, y=0.05,
                text=label,
                font=dict(size=8, family=THEME["font"], color=color),
                showarrow=False,
            )

        layout = {**LAYOUT_BASE, "height": 280, "showlegend": False,
                  "margin": dict(l=20, r=20, t=40, b=20)}
        fig.update_layout(**layout)
        return fig

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TECHNICAL CHART
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def render_technical_chart(
        self,
        df: pd.DataFrame,
        tech: dict,
        ticker: str
    ) -> go.Figure:

        if df.empty:
            return self._empty_chart("No data available")

        ticker_name = {
            "^GSPC": "S&P 500", "CL=F": "Crude Oil",
            "GC=F": "Gold", "HG=F": "Copper", "^VIX": "VIX"
        }.get(ticker, ticker)

        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            row_heights=[0.55, 0.25, 0.20],
            vertical_spacing=0.04,
            subplot_titles=[
                f"{ticker_name} â€” Price & Bands",
                "RSI (14)",
                "MACD"
            ]
        )

        # â”€â”€ Candlestick â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            name="OHLC",
            increasing_fillcolor=THEME["green"],
            increasing_line_color=THEME["green"],
            decreasing_fillcolor=THEME["red"],
            decreasing_line_color=THEME["red"],
            line_width=1,
        ), row=1, col=1)

        # â”€â”€ Bollinger Bands â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if tech:
            close = df['Close']
            bb_upper_series = close.rolling(20).mean() + 2 * close.rolling(20).std()
            bb_lower_series = close.rolling(20).mean() - 2 * close.rolling(20).std()
            bb_mid_series = close.rolling(20).mean()

            fig.add_trace(go.Scatter(
                x=df.index, y=bb_upper_series,
                name="BB Upper", line=dict(color=THEME["purple"], width=1, dash="dash"),
                opacity=0.7
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=bb_lower_series,
                name="BB Lower", line=dict(color=THEME["purple"], width=1, dash="dash"),
                fill='tonexty', fillcolor="rgba(191,95,255,0.04)", opacity=0.7
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=bb_mid_series,
                name="BB Mid", line=dict(color=THEME["purple"], width=0.5),
                opacity=0.4
            ), row=1, col=1)

            # EMAs
            ema20 = close.ewm(span=20, adjust=False).mean()
            ema50 = close.ewm(span=50, adjust=False).mean()
            ema200 = close.ewm(span=200, adjust=False).mean()

            fig.add_trace(go.Scatter(
                x=df.index, y=ema20,
                name="EMA 20", line=dict(color=THEME["cyan"], width=1)
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=ema50,
                name="EMA 50", line=dict(color=THEME["yellow"], width=1.2)
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=ema200,
                name="EMA 200", line=dict(color=THEME["orange"], width=1.5)
            ), row=1, col=1)

            # â”€â”€ RSI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            delta = close.diff()
            gain = delta.clip(lower=0).ewm(com=13, min_periods=14).mean()
            loss = (-delta.clip(upper=0)).ewm(com=13, min_periods=14).mean()
            rs = gain / loss.replace(0, np.nan)
            rsi_series = 100 - (100 / (1 + rs))

            fig.add_trace(go.Scatter(
                x=df.index, y=rsi_series,
                name="RSI", line=dict(color=THEME["cyan"], width=1.5)
            ), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color=THEME["red"], line_width=0.8, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color=THEME["green"], line_width=0.8, row=2, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color=THEME["text_muted"], line_width=0.5, row=2, col=1)

            # â”€â”€ MACD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            histogram = macd_line - signal_line

            colors = [THEME["green"] if v >= 0 else THEME["red"] for v in histogram]
            fig.add_trace(go.Bar(
                x=df.index, y=histogram,
                name="MACD Hist", marker_color=colors, opacity=0.6
            ), row=3, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=macd_line,
                name="MACD", line=dict(color=THEME["cyan"], width=1.2)
            ), row=3, col=1)
            fig.add_trace(go.Scatter(
                x=df.index, y=signal_line,
                name="Signal", line=dict(color=THEME["orange"], width=1.2)
            ), row=3, col=1)

        # â”€â”€ Layout â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        fig.update_layout(
            **LAYOUT_BASE,
            height=480,
            showlegend=True,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_rangeslider_visible=False,
        )
        fig.update_xaxes(
            gridcolor=THEME["grid"], zeroline=False,
            showspikes=True, spikecolor=THEME["cyan"], spikethickness=1
        )
        fig.update_yaxes(gridcolor=THEME["grid"], zeroline=False)
        return fig

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SENTIMENT GAUGE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def render_sentiment_gauge(self, vix: float, pcr: float) -> go.Figure:
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "indicator"}, {"type": "indicator"}]],
            subplot_titles=["VIX Fear Gauge", "Greed/Fear Index"]
        )

        # VIX gauge
        vix_color = THEME["red"] if vix > 30 else THEME["orange"] if vix > 22 else THEME["yellow"] if vix > 16 else THEME["green"]
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=vix,
            number={"font": {"size": 28, "color": vix_color, "family": THEME["font_title"]}},
            gauge={
                "axis": {"range": [5, 55], "tickfont": {"size": 9}},
                "bar": {"color": vix_color, "thickness": 0.2},
                "steps": [
                    {"range": [5, 15],  "color": "rgba(0,255,157,0.07)"},
                    {"range": [15, 25], "color": "rgba(255,214,10,0.07)"},
                    {"range": [25, 35], "color": "rgba(255,107,0,0.07)"},
                    {"range": [35, 55], "color": "rgba(255,45,85,0.07)"},
                ],
                "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
            },
        ), row=1, col=1)

        # Fear-Greed mapped from VIX
        fg = max(0, min(100, 100 - (vix - 10) / 35 * 100))
        fg_color = THEME["green"] if fg > 60 else THEME["yellow"] if fg > 40 else THEME["orange"] if fg > 20 else THEME["red"]
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=fg,
            number={"font": {"size": 28, "color": fg_color, "family": THEME["font_title"]}, "suffix": ""},
            gauge={
                "axis": {"range": [0, 100], "tickfont": {"size": 9}},
                "bar": {"color": fg_color, "thickness": 0.2},
                "steps": [
                    {"range": [0, 25],   "color": "rgba(255,45,85,0.07)"},
                    {"range": [25, 45],  "color": "rgba(255,107,0,0.07)"},
                    {"range": [45, 55],  "color": "rgba(255,214,10,0.07)"},
                    {"range": [55, 75],  "color": "rgba(0,255,157,0.07)"},
                    {"range": [75, 100], "color": "rgba(0,229,255,0.07)"},
                ],
                "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
            },
        ), row=1, col=2)

        fig.update_layout(**LAYOUT_BASE, height=200, showlegend=False,
                          margin=dict(l=10, r=10, t=25, b=5))
        return fig

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ORDER FLOW CHART
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def render_order_flow_chart(self, df: pd.DataFrame, of_data: dict) -> go.Figure:
        if df.empty:
            return self._empty_chart("No data")

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.5, 0.5], vertical_spacing=0.08,
                            subplot_titles=["On-Balance Volume (OBV)", "Chaikin Money Flow (CMF)"])

        close = df['Close']
        volume = df['Volume']
        high = df['High']
        low = df['Low']

        # OBV
        direction = close.diff().apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)
        obv_series = (volume * direction).cumsum()
        obv_colors = [THEME["green"] if v >= 0 else THEME["red"] for v in obv_series.diff().fillna(0)]

        fig.add_trace(go.Bar(
            x=df.index, y=obv_series,
            name="OBV", marker_color=obv_colors, opacity=0.7
        ), row=1, col=1)

        obv_ema = obv_series.ewm(span=10).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=obv_ema,
            name="OBV EMA", line=dict(color=THEME["cyan"], width=1.5)
        ), row=1, col=1)

        # CMF
        mf_mult = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
        mf_vol = mf_mult * volume
        cmf_series = mf_vol.rolling(20).sum() / volume.rolling(20).sum().replace(0, np.nan)
        cmf_colors = [THEME["green"] if v >= 0 else THEME["red"]
                      for v in cmf_series.fillna(0)]

        fig.add_trace(go.Bar(
            x=df.index, y=cmf_series,
            name="CMF", marker_color=cmf_colors, opacity=0.7
        ), row=2, col=1)
        fig.add_hline(y=0, line_color=THEME["text_muted"], line_width=0.8, row=2, col=1)

        fig.update_layout(**LAYOUT_BASE, height=280, showlegend=True,
                          margin=dict(l=10, r=10, t=30, b=10))
        fig.update_xaxes(gridcolor=THEME["grid"], zeroline=False)
        fig.update_yaxes(gridcolor=THEME["grid"], zeroline=False)
        return fig

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SECTOR HEATMAP
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def render_sector_heatmap(self, sector_impact: dict, scenario: str) -> go.Figure:
        sectors = list(sector_impact.keys())
        values = list(sector_impact.values())

        # Sort by impact
        pairs = sorted(zip(sectors, values), key=lambda x: x[1])
        sectors = [p[0] for p in pairs]
        values = [p[1] for p in pairs]

        colors = []
        for v in values:
            if v >= 3:   colors.append(THEME["green"])
            elif v >= 2: colors.append("#00cc7d")
            elif v >= 1: colors.append("#66ff99")
            elif v == 0: colors.append(THEME["text_muted"])
            elif v >= -1: colors.append("#ff9999")
            elif v >= -2: colors.append("#ff4d4d")
            else:         colors.append(THEME["red"])

        fig = go.Figure(go.Bar(
            y=sectors,
            x=values,
            orientation='h',
            marker_color=colors,
            marker_line_color="rgba(0,0,0,0)",
            text=[f"{'+'if v>0 else ''}{v}" for v in values],
            textposition='outside',
            textfont=dict(color=THEME["text"], size=11, family=THEME["font"]),
        ))

        title = f"Sector Impact â€” {scenario.replace('_', ' ')}" if scenario not in ("NONE", "None") else "Sector Baseline"
        fig.update_layout(
            **LAYOUT_BASE,
            title=dict(text=title, font=dict(size=12, family=THEME["font_title"], color=THEME["cyan"])),
            height=380,
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10),
            xaxis=dict(
                range=[-4, 4],
                gridcolor=THEME["grid"], zeroline=True,
                zerolinecolor=THEME["text_muted"], zerolinewidth=1,
                tickvals=[-3, -2, -1, 0, 1, 2, 3],
                ticktext=["---", "--", "-", "~", "+", "++", "+++"],
            ),
            yaxis=dict(gridcolor=THEME["grid"]),
        )
        return fig

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # MULTI-ASSET CHART
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def render_multi_asset_chart(self, raw_data: dict) -> go.Figure:
        ASSET_CONFIG = [
            ("^GSPC",    "S&P 500",      THEME["cyan"],   1.5),
            ("CL=F",     "Crude Oil",    THEME["orange"], 1.2),
            ("GC=F",     "Gold",         THEME["yellow"], 1.2),
            ("^VIX",     "VIX",          THEME["red"],    1.0),
            ("DX-Y.NYB", "Dollar Index", THEME["purple"], 1.0),
        ]

        fig = go.Figure()

        for ticker, name, color, width in ASSET_CONFIG:
            df = raw_data.get(ticker, pd.DataFrame())
            if df.empty:
                continue
            # Normalize to 100 for relative comparison
            series = df['Close']
            normalized = (series / series.iloc[0]) * 100

            fig.add_trace(go.Scatter(
                x=df.index, y=normalized,
                name=name,
                line=dict(color=color, width=width),
                hovertemplate=f"<b>{name}</b><br>%{{x}}<br>Indexed: %{{y:.1f}}<extra></extra>"
            ))

        fig.update_layout(
            **LAYOUT_BASE,
            title=dict(
                text="Multi-Asset Performance (Indexed = 100)",
                font=dict(size=12, family=THEME["font_title"], color=THEME["cyan"])
            ),
            height=320,
            showlegend=True,
            margin=dict(l=10, r=10, t=50, b=10),
            hovermode="x unified",
            xaxis=dict(gridcolor=THEME["grid"], zeroline=False,
                       showspikes=True, spikecolor=THEME["cyan"]),
            yaxis=dict(gridcolor=THEME["grid"], zeroline=False,
                       title=dict(text="Indexed Value", font=dict(size=10))),
        )
        return fig

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SHOCK FLOW DIAGRAM
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def render_shock_flow_diagram(
        self,
        scenario: str,
        shock_details: dict,
        sector_impact: dict
    ) -> go.Figure:
        """Sankey-style shock transmission diagram."""

        SCENARIO_COLORS = {
            "WAR":            THEME["red"],
            "RATE_HIKE":      THEME["orange"],
            "OIL_SHOCK":      THEME["yellow"],
            "PANDEMIC":       THEME["purple"],
            "CURRENCY_CRISIS": THEME["cyan"],
        }
        shock_color = SCENARIO_COLORS.get(scenario, THEME["cyan"])

        # Node positions: source â†’ transmission â†’ impact
        nodes = {
            "shock":     (0.1, 0.5),
            # Transmission nodes
            "vol":       (0.35, 0.8),
            "rates":     (0.35, 0.6),
            "fx":        (0.35, 0.4),
            "commodities":(0.35, 0.2),
            # Impact nodes
            "equities":  (0.65, 0.75),
            "bonds":     (0.65, 0.55),
            "gold":      (0.65, 0.35),
            "credit":    (0.65, 0.15),
            # Sector outcomes
            "winners":   (0.88, 0.7),
            "losers":    (0.88, 0.3),
        }

        labels = {
            "shock":      f"ðŸŒª {scenario.replace('_', ' ')}",
            "vol":        "ðŸ“Š Volatility â–²",
            "rates":      "ðŸ“ˆ Rates",
            "fx":         "ðŸ’± FX Moves",
            "commodities":"ðŸ›¢ï¸ Commodities",
            "equities":   "ðŸ“‰ Equities",
            "bonds":      "ðŸ›ï¸ Bonds",
            "gold":       "ðŸ¥‡ Gold",
            "credit":     "ðŸ’³ Credit",
            "winners":    "ðŸŸ¢ WINNERS",
            "losers":     "ðŸ”´ LOSERS",
        }

        fig = go.Figure()

        # Draw edges
        edges = [
            ("shock", "vol"),
            ("shock", "rates"),
            ("shock", "fx"),
            ("shock", "commodities"),
            ("vol", "equities"),
            ("rates", "equities"),
            ("rates", "bonds"),
            ("fx", "gold"),
            ("fx", "credit"),
            ("commodities", "gold"),
            ("commodities", "equities"),
            ("equities", "losers"),
            ("equities", "winners"),
            ("gold", "winners"),
            ("bonds", "winners"),
            ("credit", "losers"),
        ]

        for src, dst in edges:
            x0, y0 = nodes[src]
            x1, y1 = nodes[dst]
            fig.add_shape(
                type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                xref="paper", yref="paper",
                line=dict(color=f"rgba(0,229,255,0.2)", width=1.5),
            )

        # Draw nodes
        for key, (x, y) in nodes.items():
            color = shock_color if key == "shock" else (
                THEME["green"] if key == "winners" else
                THEME["red"] if key == "losers" else
                THEME["cyan"]
            )
            size = 20 if key in ("shock", "winners", "losers") else 12

            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode="markers+text",
                marker=dict(
                    size=size,
                    color=f"rgba({self._hex_to_rgb(color)},0.2)",
                    line=dict(color=color, width=2)
                ),
                text=[labels[key]],
                textposition="middle right" if x < 0.5 else "middle left",
                textfont=dict(size=10, color=color, family=THEME["font"]),
                showlegend=False,
                hoverinfo="skip",
            ))

        fig.update_layout(
            **LAYOUT_BASE,
            title=dict(
                text=f"Shock Transmission Flow â€” {scenario.replace('_', ' ')}",
                font=dict(size=12, family=THEME["font_title"], color=THEME["cyan"])
            ),
            height=320,
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10),
            xaxis=dict(visible=False, range=[-0.05, 1.15]),
            yaxis=dict(visible=False, range=[-0.1, 1.1]),
        )
        return fig

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # UTILITIES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _empty_chart(self, msg: str) -> go.Figure:
        fig = go.Figure()
        fig.add_annotation(
            text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
            font=dict(color=THEME["text_muted"], size=14, family=THEME["font"]),
            showarrow=False
        )
        fig.update_layout(**LAYOUT_BASE, height=300, showlegend=False,
                          margin=dict(l=10, r=10, t=30, b=10))
        return fig

    def _hex_to_rgb(self, hex_color: str) -> str:
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r},{g},{b}"
