import streamlit as st
import feedparser
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard 🚀", layout="wide")

# Styling
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; padding: 20px; }
    .news-card { background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); }
    .price-box { background-color: #1e1e2f; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

def fetch_news(url, max_entries=5):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if resp.status_code != 200:
        return []
    feed = feedparser.parse(resp.text)
    news_data = []
    for entry in feed.entries[:max_entries]:
        published_time = time.mktime(entry.published_parsed) if hasattr(entry, "published_parsed") else 0
        summary = getattr(entry, 'summary', "No summary available.")
        if len(summary) > 300:
            last_space = summary[:300].rfind(' ')
            summary = summary[:last_space] + "..." if last_space != -1 else summary[:300] + "..."
        news_data.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "published_time": published_time
        })
    return news_data

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
        st.error(f"Failed to fetch crypto prices: {e}")
        return None
    return prices

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
    "Coinvestasi": "https://coinvestasi.com/feed",
}

with st.sidebar:
    st.header("Dashboard Menu")
    st.markdown('<a href="?page=news">News Feed</a>', unsafe_allow_html=True)
    st.markdown('<a href="?page=prices">Crypto Prices</a>', unsafe_allow_html=True)

page = st.query_params.get("page", "news")
st.title("🚀 Realtime Macro & Crypto Dashboard")

if page == "news":
    feed_choice = st.sidebar.selectbox("Select News Source", list(RSS_FEEDS.keys()))
    if feed_choice == "Newest":
        all_news = []
        for feed_url in RSS_FEEDS["Newest"]:
            all_news.extend(fetch_news(feed_url, max_entries=3))
        all_news.sort(key=lambda x: x["published_time"], reverse=True)
    else:
        all_news = fetch_news(RSS_FEEDS[feed_choice], max_entries=10)
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
    if crypto_prices:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='price-box'><h3>Bitcoin</h3><p>${crypto_prices['bitcoin']['usd']:,.2f}</p><p>24h: {crypto_prices['bitcoin']['usd_24h_change']:.2f}%</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='price-box'><h3>Ethereum</h3><p>${crypto_prices['ethereum']['usd']:,.2f}</p><p>24h: {crypto_prices['ethereum']['usd_24h_change']:.2f}%</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='price-box'><h3>Solana</h3><p>${crypto_prices['solana']['usd']:,.2f}</p><p>24h: {crypto_prices['solana']['usd_24h_change']:.2f}%</p></div>", unsafe_allow_html=True)
    else:
        st.write("Unable to load crypto prices.")
