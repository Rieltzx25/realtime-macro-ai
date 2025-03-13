import streamlit as st
import feedparser
import requests
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard 🚀", layout="wide")

# ----------------------------------------------------------------
# Fungsi ambil berita dari RSS (User-Agent)
# ----------------------------------------------------------------
def fetch_news(url, max_entries=5):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if resp.status_code != 200:
        return []
    feed = feedparser.parse(resp.text)

    news_data = []
    for entry in feed.entries[:max_entries]:
        # published_time diambil dari published_parsed -> float
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_time = time.mktime(entry.published_parsed)
        else:
            published_time = 0

        # Summaries
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') else ""
        news_data.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "published_time": published_time
        })
    return news_data

# ----------------------------------------------------------------
# Fungsi ambil harga crypto (Coingecko) + error handling
# ----------------------------------------------------------------
def get_crypto_prices():
    prices = {
        "bitcoin": {"usd": 0, "usd_24h_change": 0},
        "ethereum": {"usd": 0, "usd_24h_change": 0},
        "solana": {"usd": 0, "usd_24h_change": 0}
    }
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=bitcoin,ethereum,solana"
        "&vs_currencies=usd"
        "&include_24hr_change=true"
    )
    try:
        r = requests.get(url, timeout=5).json()
        for coin in prices:
            if coin in r:
                prices[coin]["usd"] = r[coin].get("usd", 0)
                prices[coin]["usd_24h_change"] = r[coin].get("usd_24h_change", 0)
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

def display_news_items(news_list):
    if not news_list:
        st.write("Tidak ada berita.")
        return

    # HEADLINE
    top_news = news_list[0]
    other_news = news_list[1:5]

    # Headline
    dt_top = datetime.fromtimestamp(top_news["published_time"])
    st.markdown(f"### {top_news['title']}")
    st.markdown(f"[Baca selengkapnya]({top_news['link']})")
    st.caption(dt_top.strftime("%a, %d %b %Y %H:%M:%S UTC"))
    st.write(top_news['summary'])
    st.markdown("---")

    for item in other_news:
        dt_item = datetime.fromtimestamp(item["published_time"])
        st.markdown(f"- **{item['title']}**")
        st.caption(dt_item.strftime("%a, %d %b %Y %H:%M:%S UTC"))
        st.write(item['summary'])
        st.markdown(f"[Link]({item['link']})\n")


if feed_choice == "NEWEST":
    all_news = []
    for feed_url in RSS_FEEDS["NEWEST"]:
        all_news.extend(fetch_news(feed_url, max_entries=2))
    # Urutkan menurun
    all_news.sort(key=lambda x: x["published_time"], reverse=True)
    display_news_items(all_news)
else:
    news_items = fetch_news(RSS_FEEDS[feed_choice], max_entries=5)
    news_items.sort(key=lambda x: x["published_time"], reverse=True)
    display_news_items(news_items)

# ----------------------------------------------------------------
# Auto-refresh 15 detik
# ----------------------------------------------------------------
st_autorefresh(interval=15_000, limit=None, key="news_refresher")
