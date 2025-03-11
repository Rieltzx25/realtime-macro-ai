import streamlit as st
import feedparser
import time

st.set_page_config(page_title="Realtime Macro & Crypto News", layout="wide")

st.title("🌐 Realtime Macro & Crypto News Dashboard")

RSS_FEEDS = {
    "Reuters": "http://feeds.reuters.com/reuters/businessNews",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch": "https://www.marketwatch.com/rss/topstories",
    "Bloomberg": "https://www.bloomberg.com/feed/podcast/etf_report.xml",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss"
}

KEYWORDS_MACRO = ["inflation", "interest rate", "policy", "economy", "employment",
                 "Federal Reserve", "ECB", "GDP", "monetary", "BOJ", "central bank"]

KEYWORDS_CRYPTO = ["bitcoin", "ethereum", "crypto", "cryptocurrency", "blockchain", "BTC", "ETH"]

placeholder = st.empty()

def fetch_news():
    news_data = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            combined_keywords = KEYWORDS_MACRO + KEYWORDS_CRYPTO
            if any(keyword.lower() in entry.title.lower() or keyword.lower() in entry.get('summary', '').lower() for keyword in combined_keywords):
                published_time = entry.get('published', "No timestamp")
                news_data.append({
                    "source": source,
                    "title": entry.title,
                    "link": entry.link,
                    "published": published_time,
                    "summary": entry.get('summary', '')[:250] + "..."
                })
    return news_data

while True:
    news_data = fetch_news()
    with placeholder.container():
        for news in news_data[:15]:  # limit ke 15 berita terbaru
            st.subheader(f"[{news['title']}]({news['link']})")
            st.caption(f"📰 **{news['source']}** | 🕒 {news['published']}")
            st.write(f"> {news['summary']}")
            st.divider()
        st.info("🔄 **Otomatis refresh setiap 60 detik.**")
    time.sleep(60)  # Refresh setiap 60 detik otomatis
