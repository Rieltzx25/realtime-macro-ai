import streamlit as st
import feedparser
import requests
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Page Config
st.set_page_config(
    page_title="Realtime Macro & Crypto Dashboard 🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
        padding: 20px;
    }
    .sidebar .sidebar-content {
        background-color: #1e1e2f;
        color: white;
    }
    h1, h2 {
        color: #1e1e2f;
        font-family: 'Arial', sans-serif;
    }
    .news-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .news-card h3 {
        color: #1e1e2f !important;  /* Ensure headline is visible */
        margin-bottom: 5px;
    }
    .price-box {
        background-color: #1e1e2f;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .sidebar-link {
        color: #00d4ff;
        font-size: 18px;
        text-decoration: none;
        display: block;
        margin: 10px 0;
    }
    .sidebar-link:hover {
        color: #ff6f61;
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------
# Fetch News Function
# --------------------------------------
def fetch_news(url, max_entries=5):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if resp.status_code != 200:
        return []
    feed = feedparser.parse(resp.text)

    news_data = []
    for entry in feed.entries[:max_entries]:
        published_time = time.mktime(entry.published_parsed) if hasattr(entry, "published_parsed") else 0
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') else ""
        news_data.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "published_time": published_time
        })
    return news_data

# --------------------------------------
# Fetch Crypto Prices Function
# --------------------------------------
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

# --------------------------------------
# RSS Feeds
# --------------------------------------
RSS_FEEDS = {
    "Newest": [
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

# --------------------------------------
# Sidebar with Hyperlink Navigation
# --------------------------------------
with st.sidebar:
    st.header("Dashboard Menu")
    st.markdown('<a href="?page=news" class="sidebar-link">News Feed</a>', unsafe_allow_html=True)
    st.markdown('<a href="?page=prices" class="sidebar-link">Crypto Prices</a>', unsafe_allow_html=True)
    st.markdown('<a href="?page=features" class="sidebar-link">Features</a>', unsafe_allow_html=True)

# Get the page from query parameters
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["news"])[0]

# --------------------------------------
# Main Content
# --------------------------------------
st.title("🚀 Realtime Macro & Crypto Dashboard")

if page == "news":
    feed_choice = st.sidebar.selectbox("Select News Source", list(RSS_FEEDS.keys()))
    
    # Fetch and display news
    if feed_choice == "Newest":
        all_news = []
        for feed_url in RSS_FEEDS["Newest"]:
            all_news.extend(fetch_news(feed_url, max_entries=3))
        all_news.sort(key=lambda x: x["published_time"], reverse=True)
    else:
        feed_url = RSS_FEEDS[feed_choice]
        all_news = fetch_news(feed_url, max_entries=10)
        all_news.sort(key=lambda x: x["published_time"], reverse=True)

    st.subheader(f"🔥 {feed_choice} News")
    if not all_news:
        st.write("No news available.")
    else:
        for item in all_news[:10]:
            with st.container():
                st.markdown(f"<div class='news-card'><h3>{item['title']}</h3>", unsafe_allow_html=True)
                dt_item = datetime.fromtimestamp(item["published_time"])
                st.caption(dt_item.strftime("%a, %d %b %Y %H:%M:%S UTC"))
                st.write(item['summary'])
                st.markdown(f"<a href='{item['link']}' target='_blank'>Read More</a></div>", unsafe_allow_html=True)

elif page == "prices":
    st.subheader("Live Crypto Prices")
    crypto_prices = get_crypto_prices()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='price-box'><h3>Bitcoin (BTC)</h3><p>${crypto_prices['bitcoin']['usd']:,.2f}</p><p>24h: {crypto_prices['bitcoin']['usd_24h_change']:.2f}%</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='price-box'><h3>Ethereum (ETH)</h3><p>${crypto_prices['ethereum']['usd']:,.2f}</p><p>24h: {crypto_prices['ethereum']['usd_24h_change']:.2f}%</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='price-box'><h3>Solana (SOL)</h3><p>${crypto_prices['solana']['usd']:,.2f}</p><p>24h: {crypto_prices['solana']['usd_24h_change']:.2f}%</p></div>", unsafe_allow_html=True)
    
    st.info("🔄 Data refreshes every 15 seconds.")

elif page == "features":
    feature_choice = st.sidebar.selectbox("Select Feature", ["Fear and Greed Index", "Bitcoin Rainbow Chart"])
    
    if feature_choice == "Fear and Greed Index":
        st.subheader("Fear and Greed Index")
        st.markdown("[**View Fear & Greed Index**](https://alternative.me/crypto/fear-and-greed-index/)")
        st.components.v1.iframe("https://alternative.me/crypto/fear-and-greed-index/", height=600, scrolling=True)
    
    elif feature_choice == "Bitcoin Rainbow Chart":
        st.subheader("Bitcoin Rainbow Chart")
        st.markdown("[**View Bitcoin Rainbow Chart**](https://www.blockchaincenter.net/en/bitcoin-rainbow-chart/)")
        st.components.v1.iframe("https://www.blockchaincenter.net/en/bitcoin-rainbow-chart/", height=600, scrolling=True)

# Auto-refresh every 15 seconds
st_autorefresh(interval=15_000, limit=None, key="dashboard_refresher")
