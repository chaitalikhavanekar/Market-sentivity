"""
GLOBAL MARKET SHOCK ANALYZER
A quantitative dashboard for macroeconomic shock simulation and market risk analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

from data_collector import DataCollector
from analytics_engine import AnalyticsEngine
from riskometer import RiskometerModel
from shock_simulator import ShockSimulator
from sector_model import SectorImpactModel
from visualizations import Visualizer

# â”€â”€â”€ PAGE CONFIG â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.set_page_config(
    page_title="Global Market Shock Analyzer",
    page_icon="ðŸŒ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# â”€â”€â”€ CUSTOM CSS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

/* Root variables */
:root {
    --bg-primary: #050a0f;
    --bg-secondary: #0a1628;
    --bg-card: #0d1f35;
    --accent-cyan: #00e5ff;
    --accent-green: #00ff9d;
    --accent-red: #ff2d55;
    --accent-orange: #ff6b00;
    --accent-yellow: #ffd60a;
    --text-primary: #e0f4ff;
    --text-muted: #5a8aaa;
    --border: rgba(0, 229, 255, 0.15);
}

/* Global */
.stApp {
    background: var(--bg-primary) !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: var(--accent-cyan) !important;
    letter-spacing: 0.1em;
}

/* Main title */
.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem;
    font-weight: 900;
    color: var(--accent-cyan);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    text-shadow: 0 0 30px rgba(0, 229, 255, 0.5);
    margin-bottom: 0.2rem;
}

.sub-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: var(--text-muted);
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* Cards */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
}

.metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 0.3rem;
}

.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary);
}

.metric-delta-pos { color: var(--accent-green) !important; font-size: 0.85rem; }
.metric-delta-neg { color: var(--accent-red) !important; font-size: 0.85rem; }

/* Section headers */
.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--accent-cyan);
    text-transform: uppercase;
    letter-spacing: 0.25em;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 1.2rem 0 0.8rem 0;
}

/* Risk badge */
.risk-badge-on {
    display: inline-block;
    background: rgba(0, 255, 157, 0.1);
    border: 1px solid var(--accent-green);
    color: var(--accent-green);
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    padding: 0.3rem 0.8rem;
    border-radius: 4px;
    letter-spacing: 0.15em;
}

.risk-badge-off {
    display: inline-block;
    background: rgba(255, 45, 85, 0.1);
    border: 1px solid var(--accent-red);
    color: var(--accent-red);
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    padding: 0.3rem 0.8rem;
    border-radius: 4px;
    letter-spacing: 0.15em;
}

/* Sector badges */
.sector-bull { 
    color: var(--accent-green); 
    font-weight: 700;
    font-family: 'Share Tech Mono', monospace;
}
.sector-bear { 
    color: var(--accent-red); 
    font-weight: 700;
    font-family: 'Share Tech Mono', monospace;
}

/* Streamlit overrides */
div[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 0.8rem !important;
}

.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    font-family: 'Rajdhani', sans-serif !important;
}

.stButton > button {
    background: transparent !important;
    border: 1px solid var(--accent-cyan) !important;
    color: var(--accent-cyan) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    background: rgba(0, 229, 255, 0.1) !important;
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.3) !important;
}

/* Status bar */
.status-bar {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    padding-top: 0.5rem;
    margin-top: 1rem;
    letter-spacing: 0.1em;
}

.status-live {
    display: inline-block;
    width: 6px; height: 6px;
    background: var(--accent-green);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--accent-green);
    margin-right: 0.4rem;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* Plotly charts background */
.js-plotly-plot {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)


# â”€â”€â”€ CACHED DATA LOADING â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@st.cache_data(ttl=300)  # Refresh every 5 minutes
def load_market_data():
    collector = DataCollector()
    return collector.fetch_all()

def compute_analytics(raw_data):
    engine = AnalyticsEngine(raw_data)
    return engine.compute_all()


# â”€â”€â”€ MAIN APP â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def main():
    # â”€â”€ Header â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.markdown('<div class="main-title">âš¡ Global Market Shock Analyzer</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Quantitative Risk Intelligence Platform Â· v2.0</div>', unsafe_allow_html=True)
    with col_status:
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('<div class="status-bar"><span class="status-live"></span> LIVE DATA FEED ACTIVE</div>', unsafe_allow_html=True)

    # â”€â”€ Sidebar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with st.sidebar:
        st.markdown('<div class="section-header">âš™ System Controls</div>', unsafe_allow_html=True)

        if st.button("ðŸ”„ Refresh Market Data"):
            st.cache_data.clear()
            st.rerun()

        st.markdown('<div class="section-header">ðŸŒª Shock Simulator</div>', unsafe_allow_html=True)
        shock_scenario = st.selectbox(
            "Select Macro Shock Scenario",
            ["None", "WAR", "RATE_HIKE", "OIL_SHOCK", "PANDEMIC", "CURRENCY_CRISIS"],
            format_func=lambda x: {
                "None": "â€” No Shock Applied â€”",
                "WAR": "ðŸ”´ Geopolitical War",
                "RATE_HIKE": "ðŸ“ˆ Interest Rate Hike",
                "OIL_SHOCK": "ðŸ›¢ï¸ Oil Supply Shock",
                "PANDEMIC": "ðŸ¦  Pandemic / Health Crisis",
                "CURRENCY_CRISIS": "ðŸ’± Currency Crisis"
            }.get(x, x)
        )

        shock_intensity = st.slider("Shock Intensity Multiplier", 0.5, 3.0, 1.0, 0.1)

        st.markdown('<div class="section-header">ðŸ“Š Chart Settings</div>', unsafe_allow_html=True)
        chart_period = st.selectbox("Data Period", ["1mo", "3mo", "6mo", "1y"], index=1)
        primary_asset = st.selectbox(
            "Primary Asset for Technical Analysis",
            ["^GSPC", "CL=F", "GC=F", "HG=F", "^VIX"],
            format_func=lambda x: {
                "^GSPC": "S&P 500",
                "CL=F": "Crude Oil",
                "GC=F": "Gold",
                "HG=F": "Copper",
                "^VIX": "VIX"
            }.get(x, x)
        )

        st.markdown('<div class="section-header">â„¹ About</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='font-family: Share Tech Mono, monospace; font-size: 0.7rem; color: #5a8aaa; line-height: 1.8;'>
        DATA: yfinance API<br>
        INDICATORS: 30+ metrics<br>
        RISK MODEL: 5-factor weighted<br>
        REFRESH: Every 5 minutes
        </div>
        """, unsafe_allow_html=True)

    # â”€â”€ Load Data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with st.spinner("ðŸ“¡ Fetching live market data..."):
        raw_data = load_market_data()

    if not raw_data:
        st.error("âš ï¸ Failed to load market data. Please check your connection and try again.")
        return

    # â”€â”€ Compute Analytics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    engine = AnalyticsEngine(raw_data)
    indicators = engine.compute_all()

    # â”€â”€ Apply Shock Simulation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    simulator = ShockSimulator(raw_data, indicators)
    if shock_scenario != "None":
        shocked_data, shocked_indicators, shock_details = simulator.apply_shock(
            shock_scenario, intensity=shock_intensity
        )
        active_indicators = shocked_indicators
        active_raw = shocked_data
        shock_active = True
    else:
        active_indicators = indicators
        active_raw = raw_data
        shock_active = False
        shock_details = None

    # â”€â”€ Compute Risk Score â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    riskometer = RiskometerModel(active_indicators, active_raw)
    risk_result = riskometer.compute()

    sector_model = SectorImpactModel()
    viz = Visualizer()

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ROW 1 â€” RISKOMETER + MACRO OVERVIEW
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    st.markdown('<div class="section-header">ðŸŽ¯ Market Riskometer</div>', unsafe_allow_html=True)

    col_gauge, col_scores, col_macro = st.columns([2, 1.2, 1.8])

    with col_gauge:
        gauge_fig = viz.render_riskometer_gauge(risk_result)
        st.plotly_chart(gauge_fig, use_container_width=True, config={"displayModeBar": False})

    with col_scores:
        st.markdown('<div class="section-header">Component Scores</div>', unsafe_allow_html=True)
        scores = risk_result['component_scores']
        score_labels = {
            'macro': 'ðŸŒ Macro',
            'sentiment': 'ðŸ˜¨ Sentiment',
            'technical': 'ðŸ“ Technical',
            'order_flow': 'ðŸ’§ Order Flow',
            'risk_metrics': 'âš ï¸ Risk Metrics'
        }
        for key, label in score_labels.items():
            val = scores.get(key, 0.5)
            color = "#ff2d55" if val > 0.65 else "#ffd60a" if val > 0.45 else "#00ff9d"
            st.markdown(f"""
            <div style='margin-bottom:0.6rem;'>
                <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#5a8aaa;'>{label}</div>
                <div style='background:#0d1f35;border-radius:4px;height:8px;margin-top:3px;'>
                    <div style='background:{color};height:8px;border-radius:4px;width:{val*100:.0f}%;
                    box-shadow:0 0 8px {color};'></div>
                </div>
                <div style='font-family:Orbitron,monospace;font-size:0.75rem;color:{color};text-align:right;'>{val*10:.2f}/10</div>
            </div>
            """, unsafe_allow_html=True)

        mode = risk_result['market_mode']
        badge_class = "risk-badge-on" if mode == "RISK-ON" else "risk-badge-off"
        st.markdown(f'<br><div class="{badge_class}">MODE: {mode}</div>', unsafe_allow_html=True)

    with col_macro:
        st.markdown('<div class="section-header">Macro Indicators</div>', unsafe_allow_html=True)
        macro = active_indicators.get('macro', {})
        macro_display = [
            ("ðŸ›¢ï¸ Crude Oil", "oil_price", "$", ""),
            ("ðŸ¥‡ Gold", "gold_price", "$", ""),
            ("ðŸ’µ Dollar Index", "dollar_index", "", ""),
            ("ðŸ“ˆ 10Y Yield", "bond_yield", "", "%"),
        ]
        for label, key, prefix, suffix in macro_display:
            val = macro.get(key, 0)
            chg = macro.get(f"{key}_pct_chg", 0)
            delta_class = "metric-delta-pos" if chg >= 0 else "metric-delta-neg"
            arrow = "â–²" if chg >= 0 else "â–¼"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{prefix}{val:.2f}{suffix}</div>
                <div class="{delta_class}">{arrow} {abs(chg):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ROW 2 â€” SHOCK BANNER (if active)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    if shock_active and shock_details:
        st.markdown(f"""
        <div style='background:rgba(255,107,0,0.08);border:1px solid #ff6b00;border-radius:8px;
        padding:1rem 1.2rem;margin:0.5rem 0;'>
            <div style='font-family:Orbitron,monospace;font-size:0.8rem;color:#ff6b00;
            letter-spacing:0.2em;margin-bottom:0.5rem;'>
            ðŸŒª SHOCK SCENARIO ACTIVE: {shock_scenario.replace("_"," ")} (Ã—{shock_intensity:.1f})
            </div>
            <div style='font-family:Share Tech Mono,monospace;font-size:0.75rem;color:#aaa;'>
            {" Â· ".join([f"{k}: {v:+.1f}%" if 'pct' in k.lower() else f"{k}: {v:+.2f}" for k,v in list(shock_details.items())[:8]])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ROW 3 â€” TECHNICAL CHARTS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    st.markdown('<div class="section-header">ðŸ“ Technical Analysis</div>', unsafe_allow_html=True)
    col_chart, col_tech_vals = st.columns([3, 1])

    with col_chart:
        tech_fig = viz.render_technical_chart(
            raw_data.get(primary_asset, pd.DataFrame()),
            indicators.get('technical', {}).get(primary_asset, {}),
            primary_asset
        )
        st.plotly_chart(tech_fig, use_container_width=True, config={"displayModeBar": True})

    with col_tech_vals:
        st.markdown('<div class="section-header">Signal Readings</div>', unsafe_allow_html=True)
        tech = active_indicators.get('technical', {}).get(primary_asset, {})
        tech_items = [
            ("RSI(14)", "rsi", ""),
            ("MACD", "macd", ""),
            ("ADX", "adx", ""),
            ("ATR", "atr", ""),
            ("50 EMA", "ema_50", "$"),
            ("200 EMA", "ema_200", "$"),
        ]
        for label, key, prefix in tech_items:
            val = tech.get(key, 0)
            if val is None: val = 0
            # Color coding for RSI
            if key == 'rsi':
                color = "#ff2d55" if val > 70 else "#ffd60a" if val > 50 else "#00ff9d"
            elif key == 'adx':
                color = "#00e5ff" if val > 25 else "#5a8aaa"
            else:
                color = "#e0f4ff"
            st.markdown(f"""
            <div style='border-bottom:1px solid rgba(0,229,255,0.08);padding:0.5rem 0;'>
                <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#5a8aaa;'>{label}</div>
                <div style='font-family:Orbitron,monospace;font-size:1rem;color:{color};'>{prefix}{val:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        vwap = tech.get('vwap', 0) or 0
        st.markdown(f"""
        <div style='padding:0.5rem 0;'>
            <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#5a8aaa;'>VWAP</div>
            <div style='font-family:Orbitron,monospace;font-size:1rem;color:#ffd60a;'>${vwap:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ROW 4 â€” SENTIMENT + ORDER FLOW
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    col_sent, col_of = st.columns(2)

    with col_sent:
        st.markdown('<div class="section-header">ðŸ˜¨ Sentiment Panel</div>', unsafe_allow_html=True)
        sent = active_indicators.get('sentiment', {})
        vix_val = sent.get('vix', 20)
        vix_color = "#ff2d55" if vix_val > 30 else "#ffd60a" if vix_val > 20 else "#00ff9d"
        fear_label = "EXTREME FEAR" if vix_val > 35 else "FEAR" if vix_val > 25 else "NEUTRAL" if vix_val > 18 else "GREED"

        sentiment_fig = viz.render_sentiment_gauge(vix_val, sent.get('put_call_ratio', 1.0))
        st.plotly_chart(sentiment_fig, use_container_width=True, config={"displayModeBar": False})

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">VIX (Fear Index)</div>
                <div class="metric-value" style="color:{vix_color};">{vix_val:.2f}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:{vix_color};">{fear_label}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            pcr = sent.get('put_call_ratio', 1.0)
            pcr_color = "#ff2d55" if pcr > 1.2 else "#ffd60a" if pcr > 0.9 else "#00ff9d"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Put/Call Ratio</div>
                <div class="metric-value" style="color:{pcr_color};">{pcr:.2f}</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:{pcr_color};">
                {'BEARISH' if pcr > 1.2 else 'NEUTRAL' if pcr > 0.9 else 'BULLISH'}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_of:
        st.markdown('<div class="section-header">ðŸ’§ Smart Money / Order Flow</div>', unsafe_allow_html=True)
        of = active_indicators.get('order_flow', {}).get(primary_asset, {})

        of_fig = viz.render_order_flow_chart(
            raw_data.get(primary_asset, pd.DataFrame()),
            of
        )
        st.plotly_chart(of_fig, use_container_width=True, config={"displayModeBar": False})

        c1, c2, c3 = st.columns(3)
        cols = [c1, c2, c3]
        of_items = [
            ("OBV", "obv", lambda v: ("POSITIVE" if v > 0 else "NEGATIVE", "#00ff9d" if v > 0 else "#ff2d55")),
            ("CMF", "cmf", lambda v: ("INFLOW" if v > 0 else "OUTFLOW", "#00ff9d" if v > 0 else "#ff2d55")),
            ("MFI", "mfi", lambda v: ("OVERBOUGHT" if v > 80 else "OVERSOLD" if v < 20 else "NEUTRAL",
                                       "#ff2d55" if v > 80 else "#00ff9d" if v < 20 else "#ffd60a")),
        ]
        for i, (label, key, fmt) in enumerate(of_items):
            val = of.get(key, 0) or 0
            lbl_str, color = fmt(val)
            display_val = f"{val/1e6:.1f}M" if abs(val) > 1e6 else f"{val:.3f}" if abs(val) < 10 else f"{val:.1f}"
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card" style="text-align:center;">
                    <div class="metric-label">{label}</div>
                    <div style="font-family:Orbitron,monospace;font-size:0.9rem;color:{color};">{display_val}</div>
                    <div style="font-family:Share Tech Mono,monospace;font-size:0.55rem;color:{color};">{lbl_str}</div>
                </div>
                """, unsafe_allow_html=True)

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ROW 5 â€” SECTOR IMPACT + HEATMAP
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    st.markdown('<div class="section-header">ðŸ­ Sector Impact Analysis</div>', unsafe_allow_html=True)

    col_sector_table, col_sector_heat = st.columns([1, 2])

    sector_impact = sector_model.get_impact(shock_scenario if shock_active else "NONE")

    with col_sector_table:
        st.markdown("**Winners & Losers**")
        for sector, impact in sorted(sector_impact.items(), key=lambda x: x[1], reverse=True):
            if impact > 0:
                bars = "+" * min(abs(impact), 3)
                color_class = "sector-bull"
            else:
                bars = "-" * min(abs(impact), 3)
                color_class = "sector-bear"
            bar_display = bars if bars else "~"
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
            border-bottom:1px solid rgba(0,229,255,0.06);padding:0.4rem 0;'>
                <span style='font-family:Rajdhani,sans-serif;font-size:0.9rem;color:#e0f4ff;'>{sector}</span>
                <span class='{color_class}' style='font-family:Share Tech Mono,monospace;font-size:0.85rem;'>{bar_display}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_sector_heat:
        heatmap_fig = viz.render_sector_heatmap(sector_impact, shock_scenario if shock_active else "NONE")
        st.plotly_chart(heatmap_fig, use_container_width=True, config={"displayModeBar": False})

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ROW 6 â€” MULTI-ASSET OVERVIEW
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    st.markdown('<div class="section-header">ðŸŒ Multi-Asset Dashboard</div>', unsafe_allow_html=True)
    multi_fig = viz.render_multi_asset_chart(raw_data)
    st.plotly_chart(multi_fig, use_container_width=True, config={"displayModeBar": True})

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ROW 7 â€” SHOCK FLOW DIAGRAM
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    if shock_active:
        st.markdown('<div class="section-header">ðŸŒŠ Shock Transmission Flow</div>', unsafe_allow_html=True)
        flow_fig = viz.render_shock_flow_diagram(shock_scenario, shock_details, sector_impact)
        st.plotly_chart(flow_fig, use_container_width=True, config={"displayModeBar": False})

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ROW 8 â€” INDICATOR TABLE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    with st.expander("ðŸ“‹ Full Indicator Readout (All 30+ Metrics)", expanded=False):
        riskometer.display_full_table(st)

    # â”€â”€ Footer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    st.markdown("""
    <div style='text-align:center;margin-top:2rem;padding-top:1rem;
    border-top:1px solid rgba(0,229,255,0.1);
    font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#2a4a5a;'>
    GLOBAL MARKET SHOCK ANALYZER Â· QUANTITATIVE RISK INTELLIGENCE Â· DATA: yfinance Â· FOR RESEARCH PURPOSES ONLY
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
