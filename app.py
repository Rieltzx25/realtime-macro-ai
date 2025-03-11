import streamlit as st
import feedparser
import time
import requests
from datetime import datetime

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard", layout="wide")

# Judul utama
st.title("🌐 Realtime Macro & Crypto Dashboard")

# Sumber berita
RSS_FEEDS = {
    "Reuters": "http://feeds.reuters.com/reuters/businessNews",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch": "https://www.marketwatch.com/rss/topstories",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "FXStreet": "https://www.fxstreet.com/rss/news",
}

KEYWORDS = ["inflation", "interest rate", "policy", "economy", "employment",
            "Federal Reserve", "ECB", "GDP", "bitcoin", "ethereum", "solana", 
            "crypto", "cryptocurrency", "blockchain", "liquidation", "regulation"]

# Fungsi ambil harga crypto realtime
def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
    data = requests.get(url).json()
    return data

# Fungsi ambil liquidation map sederhana
def get_liquidations():
    url = "https://api.coinglass.com/api/futures/liquidation/data?symbol=BTC"
    headers = {'accept': 'application/json'}
    data = requests.get(url, headers=headers).json()
    return data

placeholder = st.empty()

def fetch_news():
    news_data = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if any(keyword.lower() in entry.title.lower() or keyword.lower() in entry.get('summary', '').lower() for keyword in KEYWORDS):
                published_parsed = entry.get('published_parsed', time.gmtime())
                published_time = datetime(*published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")
                news_data.append({
                    "source": source,
                    "title": entry.title,
                    "link": entry.link,
                    "published": published_time,
                    "summary": entry.get('summary', '')[:250] + "..."
                })
    news_data.sort(key=lambda x: x['published'], reverse=True)  # Sort by latest
    return news_data

# Loop auto-refresh setiap 30 detik
while True:
    news_data = fetch_news()
    crypto_prices = get_crypto_prices()
    liquidations = get_liquidations()

    with placeholder.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("📰 Berita Terbaru")
            for news in news_data[:20]:  # Tampilkan 20 berita terbaru
                st.markdown(f"**[{news['title']}]({news['link']})**")
                st.caption(f"📌 {news['source']} | 🕒 {news['published']}")
                st.write(f"> {news['summary']}")
                st.divider()

        with col2:
            st.subheader("📈 Harga Crypto Realtime")
            st.metric("💰 Bitcoin (BTC)", f"${crypto_prices['bitcoin']['usd']}")
            st.metric("💎 Ethereum (ETH)", f"${crypto_prices['ethereum']['usd']}")
            st.metric("🚀 Solana (SOL)", f"${crypto_prices['solana']['usd']}")

            st.subheader("🔥 Liquidation Map (BTC)")
            if liquidations.get('data'):
                total_24h = liquidations['data']['totalLiquidation']
                long_24h = liquidations['data']['longRate']
                short_24h = liquidations['data']['shortRate']
                st.write(f"💸 **Total Liquidation (24h):** ${total_24h}M")
                st.write(f"🟢 **Long Liquidation:** {long_24h}%")
                st.write(f"🔴 **Short Liquidation:** {short_24h}%")
            else:
                st.write("Data likuidasi belum tersedia.")

        st.info("🔄 **Update otomatis setiap 30 detik.**")
    
    time.sleep(30)  # Auto-refresh setiap 30 detik
