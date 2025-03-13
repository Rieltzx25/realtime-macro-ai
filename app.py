import streamlit as st
import feedparser
import requests
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard 🚀", layout="wide")

# ----------------------------------------------------------------
# Fungsi ambil berita dari RSS
# ----------------------------------------------------------------
def fetch_news(url, max_entries=5):
    feed = feedparser.parse(url)
    news_data = []
    for entry in feed.entries[:max_entries]:
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') else ""
        published = entry.get("published", "No published time")
        news_data.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "published": published
        })
    return news_data

# ----------------------------------------------------------------
# Fungsi ambil harga crypto (Coingecko) + error handling
# ----------------------------------------------------------------
def get_crypto_prices():
    # Default data jika API tidak menyediakan data
    prices = {
        "bitcoin": {"usd": 0, "usd_24h_change": 0},
        "ethereum": {"usd": 0, "usd_24h_change": 0},
        "solana": {"usd": 0, "usd_24h_change": 0}
    }

    ids = 'bitcoin,ethereum,solana'
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    try:
        response = requests.get(url, timeout=5).json()
        for coin in prices.keys():
            if coin in response:
                prices[coin]["usd"] = response[coin].get("usd", 0)
                prices[coin]["usd_24h_change"] = response[coin].get("usd_24h_change", 0)
    except Exception as e:
        print("CoinGecko API error:", e)

    return prices

# ----------------------------------------------------------------
# RSS Feeds (Makro & Crypto)
# ----------------------------------------------------------------
RSS_FEEDS = {
    "NEWEST": [
        "https://www.cnbc.com/id/20910258/device/rss/rss.html",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "https://www.reutersagency.com/feed/?best-topics=business-finance",
        "https://www.reutersagency.com/feed/?best-topics=markets",
        "https://www.investing.com/rss/news_14.rss",
        "https://www.investing.com/rss/news_301.rss",
        "https://feeds.marketwatch.com/marketwatch/topstories/",
        "https://www.bloomberg.com/feed/podcast/bloomberg-surveillance.xml",
        "https://www.ft.com/?format=rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://finance.yahoo.com/news/rssindex",
        "https://cryptoslate.com/feed/",
        "https://bitcoinmagazine.com/.rss/full/",
        "https://www.newsbtc.com/feed/",
        "https://cryptopotato.com/feed/",
        "https://coinvestasi.com/feed"
    ],
    "CNBC Economy": "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "CNBC Finance": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "Reuters Business": "https://www.reutersagency.com/feed/?best-topics=business-finance",
    "Reuters Markets": "https://www.reutersagency.com/feed/?best-topics=markets",
    "Investing.com Economy": "https://www.investing.com/rss/news_14.rss",
    "Investing.com Crypto": "https://www.investing.com/rss/news_301.rss",
    "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Coinvestasi": "https://coinvestasi.com/feed"
}

# ----------------------------------------------------------------
# Judul
# ----------------------------------------------------------------
st.title("🚀 Realtime Macro & Crypto Dashboard")

# Sidebar
feed_choice = st.sidebar.selectbox("Pilih sumber berita", list(RSS_FEEDS.keys()))

# ----------------------------------------------------------------
# Harga Crypto
# ----------------------------------------------------------------
crypto_prices = get_crypto_prices()
st.subheader("Live Crypto Prices")

prices_df = pd.DataFrame({
    'Crypto': ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Solana (SOL)'],
    'Price (USD)': [
        crypto_prices['bitcoin']['usd'],
        crypto_prices['ethereum']['usd'],
        crypto_prices['solana']['usd']
    ],
    '24h Change (%)': [
        crypto_prices['bitcoin']['usd_24h_change'],
        crypto_prices['ethereum']['usd_24h_change'],
        crypto_prices['solana']['usd_24h_change']
    ]
})
st.table(prices_df.style.format({
    "Price (USD)": "${:,.2f}",
    "24h Change (%)": "{:.2f}%"
}))
st.info("🔄 Data refreshes automatically every 15 seconds.")

# ----------------------------------------------------------------
# Berita Terbaru
# ----------------------------------------------------------------
st.subheader(f"🔥 Berita Terbaru - {feed_choice}")

if feed_choice == "NEWEST":
    all_news = []
    for feed_url in RSS_FEEDS["NEWEST"]:
        all_news.extend(fetch_news(feed_url, 2))
    all_news.sort(key=lambda x: x['published'], reverse=True)

    if len(all_news) > 0:
        top_news = all_news[0]
        other_news = all_news[1:6]
        st.markdown(f"### [{top_news['title']}]({top_news['link']})")

        # Tampilkan jam lokal WIB (opsional) atau jam feed
        wib = pytz.timezone("Asia/Jakarta")
        st.caption(datetime.now(wib).strftime('%A, %d %B %Y %H:%M WIB'))

        st.write(top_news['summary'])
        st.markdown("---")

        for news in other_news:
            st.markdown(f"- [{news['title']}]({news['link']}) ({news['published']})")

    else:
        st.write("Tidak ada berita.")
else:
    news_items = fetch_news(RSS_FEEDS[feed_choice], 5)
    if len(news_items) > 0:
        top_news = news_items[0]
        other_news = news_items[1:]
        st.markdown(f"### [{top_news['title']}]({top_news['link']})")

        # Jam WIB (opsional)
        wib = pytz.timezone("Asia/Jakarta")
        st.caption(datetime.now(wib).strftime('%A, %d %B %Y %H:%M WIB'))

        st.write(top_news['summary'])
        st.markdown("---")

        for news in other_news:
            st.markdown(f"- [{news['title']}]({news['link']}) ({news['published']})")
    else:
        st.write("Tidak ada berita.")

# ----------------------------------------------------------------
# Auto-refresh 15 detik
# ----------------------------------------------------------------
count = st_autorefresh(interval=15_000, limit=None, key="news_refresher")
