import streamlit as st
import feedparser
from textblob import TextBlob

st.set_page_config(page_title="Realtime Macro News", layout="wide")

st.title("🌐 Realtime Macro News Dashboard")

RSS_FEEDS = {
    "Reuters": "http://feeds.reuters.com/reuters/businessNews",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch": "https://www.marketwatch.com/rss/topstories",
    "Bloomberg": "https://www.bloomberg.com/feed/podcast/etf_report.xml"
}

KEYWORDS = ["inflation", "interest rate", "policy", "economy", "employment", "monetary"]

def summarize(text):
    blob = TextBlob(text)
    sentences = blob.sentences
    if len(sentences) > 1:
        return ' '.join([str(sentences[0]), str(sentences[1])])
    return text

for source, url in RSS_FEEDS.items():
    feed = feedparser.parse(url)
    with st.expander(f"🗞️ **{source}**"):
        count = 0
        for entry in feed.entries:
            if any(keyword.lower() in entry.title.lower() for keyword in KEYWORDS):
                st.markdown(f"### [{entry.title}]({entry.link})")
                if hasattr(entry, 'summary'):
                    summary = summarize(entry.summary)
                    st.write(f"> {summary}")
                count += 1
                if count == 5:
                    break  # Batasi 5 berita per sumber
