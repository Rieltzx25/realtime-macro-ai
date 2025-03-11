import streamlit as st
import feedparser

st.title("Realtime Macro News")

RSS_FEEDS = {
    "Reuters": "http://feeds.reuters.com/reuters/businessNews",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
}

KEYWORDS = ["inflation", "interest rate", "policy", "economy"]

for source, url in RSS_FEEDS.items():
    feed = feedparser.parse(url)
    st.header(f"📌 {source}")
    for entry in feed.entries[:10]:  # Ambil 10 berita terbaru
        if any(keyword.lower() in entry.title.lower() for keyword in KEYWORDS):
            st.markdown(f"- [{entry.title}]({entry.link})")
