import streamlit as st
import feedparser
import requests
from datetime import datetime
import time

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard", layout="wide")

st.title("🌐 Realtime Macro & Crypto Dashboard")

RSS_FEEDS = {
    "Reuters": "http://feeds.reuters.com/reuters/businessNews",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch": "https://www.marketwatch.com/rss/topstories",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss"
}

KEYWORDS = [
    "inflation", "interest rate", "policy", "economy", "employment", 
    "Federal Reserve", "ECB", "GDP", "bitcoin", "ethereum", "solana", 
    "crypto", "cryptocurrency", "blockchain", "liquidation", "regulation", "tariff"
]

def fetch_news():
    news_data = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if any(keyword.lower() in entry.title.lower() or keyword.lower() in entry.get('summary', '').lower() for keyword in KEYWORDS):
                published_time = entry.get('published', 'N/A')
                news_data.append({
                    "source": source,
                    "title": entry.title,
                    "link": entry.link,
                    "published": published_time,
                    "summary": entry.get('summary', 'No summary available.')[:250] + "..."
                })
    news_data.sort(key=lambda x: x['published'], reverse=True)
    return news_data

def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
    try:
        data = requests.get(url).json()
    except:
        data = {'bitcoin': {'usd': 'N/A'}, 'ethereum': {'usd': 'N/A'}, 'solana': {'usd': 'N/A'}}
    return data

# Streamlit app layout
st.set_page_config(page_title="Realtime Macro & Crypto Dashboard", layout="wide")
st.title("🌐 Realtime Macro & Crypto Dashboard")

news_placeholder = st.empty()

# Auto refresh tiap 15 detik
while True:
    news_data = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if any(keyword.lower() in entry.title.lower() or keyword.lower() in entry.get('summary', '').lower() for keyword in KEYWORDS):
                news_data.append({
                    "source": source,
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get('published', 'N/A'),
                    "summary": entry.get('summary', 'No summary available.')[:250] + "..."
                })

    news_data.sort(key=lambda x: x['published'], reverse=True)

    crypto_prices = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd").json()

    st.subheader("📰 Berita Ekonomi & Crypto Terbaru")
    for news in news_data[:20]:  # Menampilkan 20 berita terbaru
        st.markdown(f"**[{news['title']}]({news['link']})**")
        st.caption(f"📌 {news['source']} | 🕒 {news['published']}")
        st.write(f"> {news['summary']}")
        st.divider()

    # Sidebar untuk harga crypto
    st.sidebar.title("Crypto Market 📈")
    st.sidebar.metric("Bitcoin (BTC)", f"${crypto_prices['bitcoin']['usd']}")
    st.sidebar.metric("Ethereum (ETH)", f"${crypto_prices['ethereum']['usd']}")
    st.sidebar.metric("Solana (SOL)", f"${crypto_prices['solana']['usd']}")

    st.info("🔄 **Update otomatis setiap 15 detik.**")

    time.sleep(15)
