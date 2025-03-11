import streamlit as st
import feedparser
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard", layout="wide")

st.title("🚀 Realtime Macro & Crypto Dashboard")

# Comprehensive RSS feeds
RSS_FEEDS = {
    "CNBC - Economy": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "CNBC - Finance": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "Reuters - Business": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
    "Reuters - Markets": "http://feeds.reuters.com/reuters/businessNews",
    "Investing.com - Economy": "https://www.investing.com/rss/news_14.rss",
    "Investing.com - Crypto": "https://www.investing.com/rss/news_301.rss",
    "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
    "Bloomberg Markets": "https://www.bloomberg.com/feed/podcast/bloomberg-markets.xml",
    "Financial Times": "https://www.ft.com/?format=rss",
    "CoinDesk - Crypto": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
}

# Fetch RSS feed function
def fetch_news(feed_url):
    news_feed = feedparser.parse(feed_url)
    news_items = []
    for entry in news_feed.entries[:7]:
        published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M")
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": published,
            "summary": entry.summary[:300] + "..."
        })
    return news_items

# Crypto price fetcher
def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin,ethereum,solana',
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }
    response = requests.get(url, params=params)
    return response.json()

# UI Layout
col1, col2 = st.columns([3, 1])

# News display
with col1:
    tabs = st.tabs(RSS_FEEDS.keys())
    for tab, (source, url) in zip(tabs, RSS_FEEDS.items()):
        with tab:
            news = fetch_news(url)
            for item in news:
                st.markdown(f"### [{item['title']}]({item['link']})")
                st.caption(f"🕑 {item['published']}")
                st.write(item['summary'])

# Crypto prices
with col2:
    st.subheader("💱 Live Crypto Prices")
    crypto_prices = get_crypto_prices()
    df = pd.DataFrame.from_dict(crypto_prices, orient='index')
    df.columns = ['Price (USD)', '24h Change (%)']
    st.table(df)

    st.info("ℹ️ Data refreshes automatically every 15 seconds.")

# Auto-refresh (15 seconds)
st_autorefresh = st.empty()
st_autorefresh.markdown("<meta http-equiv='refresh' content='15'>", unsafe_allow_html=True)
