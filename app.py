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
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') else "Tidak ada ringkasan."
        published = entry.get("published", "Tidak ada tanggal")
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
st.subheader("📈 Live Crypto Prices")

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

# Sidebar untuk memilih sumber berita
st.sidebar.header("📰 Pilih sumber berita")
selected_feed = st.sidebar.selectbox("Sumber Berita:", RSS_FEEDS.keys())

# Tampilkan berita terbaru
def display_news(selected_feed):
    news_items = fetch_news(RSS_FEEDS[selected_feed], 5)
    st.subheader(f"🗞️ Berita Terkini - {selected_feed}")
    for item in news_items:
        with st.expander(f"{item['title']} [{item['published']}]", expanded=False):
            st.write(item['summary'])
            st.markdown(f"[Baca selengkapnya disini]({item['link']})")

# Tampilkan berita
display_news(selected_feed)

# Informasi waktu update
st.sidebar.write("📅", datetime.now().strftime("%A, %d %B %Y"))
st.sidebar.write("⏰", datetime.now().strftime("%H:%M:%S"))
st.sidebar.info("🔃 Halaman diperbarui otomatis setiap 15 detik.")

# Auto-refresh setiap 15 detik
import time

with st.empty():
    time.sleep(15)
    st.experimental_rerun()
