import streamlit as st
import feedparser
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
from textblob import TextBlob
import os

#####################################
# 1) CONFIG STREAMLIT & CSS STYLING
#####################################
st.set_page_config(
    page_title="Realtime Macro & Crypto Dashboard 🚀",
    layout="wide"
)

# Tailwind-ish custom CSS
st.markdown("""
<style>
/* Global gradient bg */
.main {
    background: linear-gradient(to bottom right, #0f172a, #1e293b);
    color: #f1f5f9;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
/* Hero Section */
.hero {
    background: linear-gradient(to right, #f59e0b, #fbbf24);
    padding: 2rem;
    border-radius: 1rem;
    margin-bottom: 1rem;
    color: #1e293b;
}
.hero h1 {
    font-size: 2rem;
    font-weight: 700;
}
.hero p {
    font-size: 1rem;
}
/* Headings color */
h1, h2, h3, h4 {
  color: #fbbf24 !important;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}
/* Crypto card */
.crypto-card {
    background: #1e293b;
    border: 1px solid #475569;
    border-radius: 0.75rem;
    padding: 1rem;
    text-align: center;
    transition: transform 0.2s ease-in-out;
    margin-bottom: 1rem;
}
.crypto-card:hover {
    transform: scale(1.02);
}
.crypto-price {
    font-size: 1.5rem;
    font-weight: 600;
}
.crypto-change.negative {
    color: #ef4444;
}
.crypto-change.positive {
    color: #22c55e;
}
/* News card */
.news-card {
    background: #1e293b;
    border: 1px solid #475569;
    border-radius: 0.75rem;
    padding: 1rem;
    transition: all 0.2s ease;
    margin-bottom: 1rem;
}
.news-card:hover {
    background: #2e3a4e;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
.news-headline {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}
.news-summary {
    font-size: 0.85rem;
    color: #cbd5e1;
}
.news-timestamp {
    font-size: 0.75rem;
    color: #94a3b8;
}
</style>
""", unsafe_allow_html=True)

#####################################
# 2) RSS FEEDS & FEATURES
#####################################
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
        "https://coinvestasi.com/feed",
        "https://www.imf.org/external/rss/feeds.aspx?category=News",
        "https://www.federalreserve.gov/feeds/press_all.xml",
        "https://blogs.worldbank.org/rss.xml",
        "https://www.theblockcrypto.com/rss.xml",
        "https://cryptobriefing.com/feed/",
        "https://bitcoinist.com/feed/"
    ],
    "IMF News": "https://www.imf.org/external/rss/feeds.aspx?category=News",
    "Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "World Bank": "https://blogs.worldbank.org/rss.xml",
    "The Block Crypto": "https://www.theblockcrypto.com/rss.xml",
    "Crypto Briefing": "https://cryptobriefing.com/feed/",
    "Bitcoinist": "https://bitcoinist.com/feed/",
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
    "Fear and Greed Index": None,
    "Bitcoin Rainbow Chart": None
}
NEWS_SOURCES = {k: v for k, v in RSS_FEEDS.items() if v is not None}
FEATURES = ["Fear and Greed Index", "Bitcoin Rainbow Chart"]

#####################################
# 3) FUNGSI UTAMA (NEWS, CRYPTO, dsb)
#####################################
def fetch_news(url, max_entries=5):
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        news_data = []
        for entry in feed.entries[:max_entries]:
            published_time = time.mktime(entry.published_parsed) if hasattr(entry, "published_parsed") else 0
            summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') and entry.summary else "No summary."
            news_data.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summary,
                "published_time": published_time
            })
        return news_data
    except:
        return []

def get_crypto_prices():
    prices = {"bitcoin": {}, "ethereum": {}, "solana": {}}
    url = ("https://api.coingecko.com/api/v3/simple/price"
           "?ids=bitcoin,ethereum,solana"
           "&vs_currencies=usd"
           "&include_24hr_change=true")
    try:
        data = requests.get(url, timeout=5).json()
        for coin in prices:
            if coin in data:
                prices[coin] = {
                    "usd": data[coin].get("usd", 0),
                    "usd_24h_change": data[coin].get("usd_24h_change", 0)
                }
    except:
        pass
    return prices

def get_bitcoin_history(days=30):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    r = requests.get(url).json()
    dates = [datetime.utcfromtimestamp(p[0]/1000).strftime('%Y-%m-%d') for p in r['prices']]
    prices = [p[1] for p in r['prices']]
    return dates, prices

def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        if blob.sentiment.polarity > 0:
            return "Positif"
        elif blob.sentiment.polarity < 0:
            return "Negatif"
        else:
            return "Netral"
    except:
        return "Tidak Diketahui"

def display_news_items(news_list):
    if not news_list:
        st.write("Tidak ada berita.")
        return
    for item in news_list:
        dt_item = datetime.fromtimestamp(item["published_time"])
        senti = analyze_sentiment(item["summary"])
        st.markdown(f"""
        <div class="news-card">
            <p class="news-headline">{item['title']}</p>
            <p class="news-timestamp">
              {dt_item.strftime('%a, %d %b %Y %H:%M:%S UTC')} 
              | <b>SENTIMEN: {senti}</b>
            </p>
            <p class="news-summary">{item['summary']}</p>
            <p><a href="{item['link']}" target="_blank" style="color:#fbbf24;">🔗 Read More</a></p>
        </div>
        """, unsafe_allow_html=True)

#####################################
# 4) STATE: CRYPTO AUTO-REFRESH
#####################################
if "crypto_prices" not in st.session_state:
    st.session_state.crypto_prices = get_crypto_prices()
if "last_price_refresh" not in st.session_state:
    st.session_state.last_price_refresh = time.time()

if time.time() - st.session_state.last_price_refresh >= 15:
    st.session_state.crypto_prices = get_crypto_prices()
    st.session_state.last_price_refresh = time.time()

#####################################
# 5) TAMPILAN (LAYOUT UTAMA)
#####################################

# Hero Section
st.markdown("""
<div class="hero">
    <h1>Realtime Macro & Crypto Dashboard 🚀</h1>
    <p>Keep track of the latest macroeconomic news and crypto prices in one place.</p>
</div>
""", unsafe_allow_html=True)

# Tampilkan 3 crypto
st.subheader("Live Crypto Prices")
col1, col2, col3 = st.columns(3)
cryptos = [
    ("Bitcoin (BTC)", "bitcoin"),
    ("Ethereum (ETH)", "ethereum"),
    ("Solana (SOL)", "solana"),
]
for (name, coin_key), col in zip(cryptos, [col1, col2, col3]):
    with col:
        info = st.session_state.crypto_prices.get(coin_key, {})
        price = info.get("usd", 0)
        change = info.get("usd_24h_change", 0)
        change_class = "negative" if change < 0 else "positive"
        st.markdown(f"""
        <div class="crypto-card">
            <h4 style="margin-bottom:0.5rem;">{name}</h4>
            <p class="crypto-price">${price:,.2f}</p>
            <p class="crypto-change {change_class}">{change:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

st.write("Data refreshes automatically every 15 seconds.")
st.write("---")

# Navigation (News Feed / Features)
section = st.radio("Navigation", ["News Feed", "Features"], horizontal=True)

if section == "News Feed":
    st.subheader("📰 Latest News")

    feed_choice = st.selectbox("Pilih sumber berita:", list(NEWS_SOURCES.keys()))
    keyword = st.text_input("Cari berita:")

    if feed_choice == "NEWEST":
        # Kumpulkan feed 'NEWEST'
        all_news = []
        for f in RSS_FEEDS["NEWEST"]:
            all_news.extend(fetch_news(f, max_entries=3))
    else:
        feed_url = NEWS_SOURCES[feed_choice]
        all_news = fetch_news(feed_url, max_entries=10)

    # Sort & Filter
    all_news.sort(key=lambda x: x["published_time"], reverse=True)
    if keyword:
        all_news = [n for n in all_news if keyword.lower() in n["title"].lower()]

    display_news_items(all_news)

elif section == "Features":
    st.subheader("Fitur Tambahan")
    feature_choice = st.selectbox("Pilih Fitur", ["Bitcoin Chart", "Fear and Greed Index", "Bitcoin Rainbow Chart"])

    if feature_choice == "Bitcoin Chart":
        st.markdown("### 📈 Bitcoin Price (30 Day Chart)")
        dts, prcs = get_bitcoin_history(30)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dts, y=prcs, name="BTC", line=dict(color='gold')))
        fig.update_layout(
            title="Harga Bitcoin - 30 Hari",
            xaxis_title="Tanggal",
            yaxis_title="USD",
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font_color="white",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif feature_choice == "Fear and Greed Index":
        st.markdown("### Fear and Greed Index")
        st.warning("Iframe is blocked by the site. Click link below to view.")
        st.markdown("[Visit Fear and Greed Index](https://alternative.me/crypto/fear-and-greed-index/)")

    elif feature_choice == "Bitcoin Rainbow Chart":
        st.markdown("### Bitcoin Rainbow Chart")
        st.warning("Iframe is blocked by the site. Click link below to view.")
        st.markdown("[Visit Bitcoin Rainbow Chart](https://www.blockchaincenter.net/en/bitcoin-rainbow-chart/)")
