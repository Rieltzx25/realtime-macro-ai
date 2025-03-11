import streamlit as st
import feedparser
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard 🚀", layout="wide")

# Fungsi ambil berita dari RSS dengan error handling
def fetch_news(url, max_entries=5):
    feed = feedparser.parse(url)
    news_data = []
    for entry in feed.entries[:max_entries]:
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') else "Tidak ada ringkasan tersedia."
        published = entry.get("published", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        news_data.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "published": published
        })
    return news_data

# Fungsi ambil harga crypto realtime (Coingecko) dengan error handling
def get_crypto_prices():
    ids = 'bitcoin,ethereum,solana'
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url).json()
    prices = {}
    for crypto in ['bitcoin', 'ethereum', 'solana']:
        if crypto in response:
            prices[crypto] = response[crypto]
        else:
            prices[crypto] = {'usd': 'N/A', 'usd_24h_change': 'N/A'}
    return prices

# RSS Feeds (makroekonomi & crypto)
RSS_FEEDS = {
    "CNBC Economy": "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "CNBC Finance": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "Reuters Business": "https://www.reutersagency.com/feed/?best-topics=business-finance",
    "Reuters Markets": "https://www.reutersagency.com/feed/?best-topics=markets",
    "Investing.com Economy": "https://www.investing.com/rss/news_14.rss",
    "Investing.com Crypto": "https://www.investing.com/rss/news_301.rss"
}

# Judul
st.title("🚀 Realtime Macro & Crypto Dashboard")

# Crypto Prices
crypto_prices = get_crypto_prices()
st.subheader("💹 Live Crypto Prices")

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

# Berita terbaru
def display_news():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📰 Berita Terkini")
        feed_choice = st.selectbox("Pilih sumber berita", options=list(RSS_FEEDS.keys()))
        news_items = fetch_news(RSS_FEEDS[feed_choice], 5)
        for item in news_items:
            with st.expander(f"{item['title']} [{item['published']}]"):
                st.write(item['summary'])
                st.markdown(f"[🔗 Baca lengkap disini]({item['link']})")

    with col2:
        st.subheader("🗓️ Informasi")
        st.markdown("📅 " + datetime.now().strftime('%A, %d %B %Y'))
        st.markdown("⏰ " + datetime.now().strftime('%H:%M:%S'))
        st.markdown("🔃 Halaman diperbarui otomatis.")

# Tampilkan berita terbaru
display_news()

# Auto-refresh setiap 15 detik
st_autorefresh = st.empty()

import time
with st_autorefresh:
    time.sleep(15)
    st.experimental_rerun()
