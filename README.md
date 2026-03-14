# 🌐 Global Market Shock Analyzer

A quantitative financial analytics dashboard for simulating macroeconomic shocks and analyzing market risk across 30+ indicators.

## Architecture

```
global_market_shock_analyzer/
├── app.py                  # Main Streamlit dashboard
├── data_collector.py       # yfinance data acquisition layer
├── analytics_engine.py     # Technical + order flow indicator computation
├── riskometer.py           # 5-factor weighted risk model
├── shock_simulator.py      # Macro shock scenario engine
├── sector_model.py         # Sector impact mapping
├── visualizations.py       # All Plotly chart renderers
└── requirements.txt
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the dashboard
streamlit run app.py
```

## Features

### Data Sources (via yfinance)
- Crude Oil (`CL=F`)
- Gold (`GC=F`)
- Copper (`HG=F`)
- S&P 500 (`^GSPC`)
- VIX (`^VIX`)
- Dollar Index (`DX-Y.NYB`)
- 10Y Treasury Yield (`^TNX`)

### Technical Indicators (30+)
- RSI, MACD, Bollinger Bands
- EMA 20/50/200
- ATR, ADX, VWAP
- Stochastic %K, ROC

### Order Flow
- OBV (On-Balance Volume)
- CMF (Chaikin Money Flow)
- MFI (Money Flow Index)

### Riskometer Model
```
Risk Score = 0.30 × Macro
           + 0.20 × Sentiment
           + 0.20 × Technical
           + 0.15 × Order Flow
           + 0.15 × Risk Metrics
```
Output: 0–10 score + Risk-On/Off mode

### Shock Scenarios
| Scenario | Key Effects |
|----------|------------|
| WAR | Oil +3%, Gold +2%, Stocks -2.5%, VIX +5 |
| RATE_HIKE | Stocks -3%, Dollar +1.5%, Yield +100bps |
| OIL_SHOCK | Oil +5%, Airlines -4%, Energy +3% |
| PANDEMIC | Stocks -6%, VIX +15, Oil -8% |
| CURRENCY_CRISIS | Dollar +2.5%, EM -3%, Gold +2.5% |

## Disclaimer
For research and educational purposes only. Not financial advice.
