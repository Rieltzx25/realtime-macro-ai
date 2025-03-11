import streamlit as st
import feedparser
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard 🚀", layout="wide")

# Fungsi ambil berita dari RSS
def fetch_news(url, max_entries=5):
    feed = feedparser.parse(url)
    news_data = []
    for entry in feed.entries[:max_entries]:
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') else ""
        published = entry.get("published", "")
        news_data.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "published": published
        })
    return news_data

# Fungsi ambil harga crypto realtime (Coingecko)
def get_crypto_prices():
    ids = 'bitcoin,ethereum,solana'
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url).json()
    return response

# RSS Feeds (makroekonomi & crypto)
RSS_FEEDS = {
    "CNBC Economy": "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "CNBC Finance": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "Reuters Business": "https://www.reutersagency.com/feed/?best-topics=business-finance",
    "Reuters Markets": "https://www.reutersagency.com/feed/?best-topics=markets",
    "Investing.com Economy": "https://www.investing.com/rss/news_14.rss",
    "Investing.com Crypto": "https://www.investing.com/rss/news_301.rss",
    "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
    "Bloomberg Markets": "https://www.bloomberg.com/feed/podcast/bloomberg-surveillance.xml",
    "Financial Times": "https://www.ft.com/?format=rss",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "CryptoSlate": "https://cryptoslate.com/feed/",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/",
    "NewsBTC": "https://www.newsbtc.com/feed/",
    "CryptoPotato": "https://cryptopotato.com/feed/"
}

# Judul
st.title("🚀 Realtime Macro & Crypto Dashboard")

# Crypto Prices
crypto_prices = get_crypto_prices()
st.subheader("Live Crypto Prices")

prices_df = pd.DataFrame({
    'Crypto': ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Solana (SOL)'],
    'Price (USD)': [crypto_prices['bitcoin']['usd'], crypto_prices['ethereum']['usd'], crypto_prices['solana']['usd']],
    '24h Change (%)': [
        crypto_prices['bitcoin']['usd_24h_change'],
        crypto_prices['ethereum']['usd_24h_change'],
        crypto_prices['solana']['usd_24h_change']
    ]
})
st.table(prices_df.style.format({"Price (USD)": "${:,.2f}", "24h Change (%)": "{:.2f}%"}))
st.info('🔄 Data refreshes automatically every 15 seconds.')

# Auto-refresh setiap 15 detik
st_autorefresh = st.empty()

# Berita terbaru
def display_news():
    st.subheader("Latest Macro & Crypto News")
    for source, url in RSS_FEEDS.items():
        news_items = fetch_news(url, 3)
        st.markdown(f"### 📌 {source}")
        for item in news_items:
            st.write(f"[{item['title']}]({item['link']})")
            st.caption(f"{item['published']}")
            st.write(f"{item['summary']}")
            st.divider()

# Tampilkan berita terbaru
display_news()

# Refresh otomatis tiap 15 detik tanpa reload penuh
import time

with st_autorefresh:
    time.sleep(15)
    st.experimental_rerun()
