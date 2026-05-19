# Realtime Macro & Crypto Dashboard

A Streamlit dashboard for tracking crypto prices, macro news, and market sentiment in real time.

Built to stay on top of market conditions without juggling multiple tabs.

---

## What it does

- **Live crypto prices** — BTC, ETH, SOL with 24h change (CoinGecko API, refreshes every 15s)
- **Multi-source news feed** — pulls from CNBC, Reuters, CoinDesk, Cointelegraph, Yahoo Finance, and more
- **Sentiment analysis** — TextBlob scores each headline as Bullish / Bearish / Neutral
- **Bitcoin Rainbow Chart** — logarithmic regression bands (Plotly)
- **Fear & Greed Index** — visual gauge
- **Technical indicators** — RSI, MACD, moving averages overview

---

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## News sources

23 RSS feeds including:

| Source | Category |
|--------|----------|
| CNBC Economy / Finance | Macro |
| Reuters Business / Markets | Macro |
| IMF, Federal Reserve, World Bank | Macro / Policy |
| CoinDesk, Cointelegraph, The Block | Crypto |
| Coinvestasi | Crypto (Indonesian) |
| Yahoo Finance, MarketWatch | General Finance |

---

## Stack

```
streamlit
feedparser
requests
plotly
textblob
numpy
pandas
streamlit-autorefresh
```

---

## Folder structure

```
realtime-macro-ai/
├── app.py              # main dashboard (single-file app)
├── cat_logo.webp       # sidebar logo
├── requirements.txt
└── assets/
```
