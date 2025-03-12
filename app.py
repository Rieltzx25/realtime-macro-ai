import streamlit as st
import feedparser
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard 🚀", layout="wide")

# CSS Animasi dan gaya tambahan
st.markdown("""
<style>
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}

.headline {
    font-size: 24px;
    font-weight: bold;
    animation: fadeIn 1s ease-in-out;
}

.news-item {
    padding: 10px;
    border-radius: 5px;
    transition: transform 0.3s ease;
}

.news-item:hover {
    transform: scale(1.03);
    background-color: #f1f1f1;
}
</style>
""", unsafe_allow_html=True)

# Fungsi ambil berita dari RSS
def fetch_news(url, max_entries=5):
    feed = feedparser.parse(url)
    news_data = []
    for entry in feed.entries[:max_entries]:
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') else ""
        published = entry.get("published", datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
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
    "Investing.com Economy": "https://www.investing.com/rss/news_14.rss",
    "Investing.com Crypto": "https://www.investing.com/rss/news_301.rss",
    "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
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
st.subheader("📊 Live Crypto Prices")

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

# Berita terbaru otomatis
all_news = []
for source, url in RSS_FEEDS.items():
    all_news.extend(fetch_news(url, 3))

# Urutkan berita berdasarkan waktu publikasi
all_news.sort(key=lambda x: x['published'], reverse=True)

# Berita utama terbaru (headline besar)
st.markdown(f"<div class='headline'>🔥 {all_news[0]['title']} [{all_news[0]['published']}]</div>", unsafe_allow_html=True)
st.write(f"{all_news[0]['summary']} [Read more]({all_news[0]['link']})")
st.divider()

# Tampilkan berita lainnya
st.subheader("📰 Berita Terbaru Lainnya")
for news in all_news[1:10]:
    st.markdown(f"<div class='news-item'>🔹 [{news['title']}]({news['link']}) <br><small>{news['published']}</small><br>{news['summary']}</div>", unsafe_allow_html=True)

# Informasi waktu update
st.sidebar.markdown(f"⏰ Last updated: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S')}")
