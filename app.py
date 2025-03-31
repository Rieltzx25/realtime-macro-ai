import streamlit as st
import feedparser
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os
import plotly.graph_objects as go
from textblob import TextBlob

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard 🚀", layout="wide")

#########################################
# 1) CSS Langsung (untuk tampilan gelap)
#########################################
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #1e1e2f 0%, #2a2a4a 100%);
}
/* Kartu berita */
.news-card {
    background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
    padding: 15px; border-radius: 15px; margin-bottom: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    border: 1px solid transparent;
    background-image: linear-gradient(#1a1a1a, #1a1a1a),
                      linear-gradient(45deg, #FF4500, #FFD700);
    background-origin: border-box; background-clip: padding-box, border-box;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.news-card:hover {
    box-shadow: 0 6px 12px rgba(255, 255, 255, 0.15);
    transform: translateY(-3px);
}
.news-headline {
    color: #FFFFFF; font-size: 20px; font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}
.news-summary {
    color: #CCCCCC; font-size: 14px;
}
.news-timestamp {
    color: #888; font-size: 12px;
}

/* Kartu Crypto */
.crypto-card {
    background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
    padding: 15px; border-radius: 20px; text-align: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    border: 1px solid transparent;
    background-image: linear-gradient(#1a1a1a, #1a1a1a),
                      linear-gradient(45deg, #FFD700, #00FF00);
    background-origin: border-box; background-clip: padding-box, border-box;
    transition: transform 0.2s ease-in-out;
}
.crypto-card:hover {
    transform: scale(1.02);
}
.crypto-name {
    font-size: 20px; font-weight: bold;
}
.crypto-name.bitcoin { color: #FFD700; }
.crypto-name.ethereum, .crypto-name.solana { color: #FFFFFF; }
.crypto-price {
    font-size: 18px; font-weight: bold; color: #FFFFFF;
}
.crypto-change {
    font-size: 16px;
}
.crypto-change.negative { color: #FF0000; }
.crypto-change.positive { color: #00FF00; }

h1 {
    color: #FFD700 !important;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}
h2 {
    color: #00FF00 !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}
</style>
""", unsafe_allow_html=True)

###################################
# 2) RSS FEEDS & CONFIG (UTAMA)
###################################
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

#############################
# 3) FUNCTION UTILITAS
#############################
def fetch_news(url, max_entries=5):
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        data = []
        for entry in feed.entries[:max_entries]:
            pub_t = time.mktime(entry.published_parsed) if hasattr(entry, "published_parsed") else 0
            summary = entry.summary[:300]+"..." if getattr(entry, 'summary', None) else "No summary."
            data.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summary,
                "published_time": pub_t
            })
        return data
    except:
        return []

def get_crypto_prices():
    coins = {"bitcoin": {}, "ethereum": {}, "solana": {}}
    url = ("https://api.coingecko.com/api/v3/simple/price"
           "?ids=bitcoin,ethereum,solana"
           "&vs_currencies=usd"
           "&include_24hr_change=true")
    try:
        data = requests.get(url, timeout=5).json()
        for c in coins:
            if c in data:
                coins[c] = {
                    "usd": data[c].get("usd", 0),
                    "usd_24h_change": data[c].get("usd_24h_change", 0)
                }
    except:
        pass
    return coins

def get_bitcoin_history(days=30):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    r = requests.get(url).json()
    dates = [datetime.utcfromtimestamp(pt[0]/1000).strftime('%Y-%m-%d') for pt in r['prices']]
    prices = [pt[1] for pt in r['prices']]
    return dates, prices

from textblob import TextBlob
def analyze_sentiment(txt):
    try:
        blob = TextBlob(txt)
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
        <div class='news-card'>
          <p class='news-headline'>{item['title']}</p>
          <p class='news-timestamp'>
            {dt_item.strftime('%a, %d %b %Y %H:%M:%S UTC')} 
            | <strong>SENTIMEN: {senti}</strong>
          </p>
          <p class='news-summary'>{item['summary']}</p>
          <p><a href='{item['link']}' target='_blank'>🔗 Baca Selengkapnya</a></p>
        </div>
        """, unsafe_allow_html=True)

def show_utc_wib_time():
    """Mengembalikan jam UTC & WIB dalam string."""
    now_utc = datetime.utcnow()
    utc_str = now_utc.strftime("%H:%M:%S")
    wib = (now_utc.hour + 7) % 24
    wib_str = f"{wib:02}:{now_utc.minute:02}:{now_utc.second:02}"
    return f"UTC: {utc_str} | WIB: {wib_str}"

#########################################
# 4) SIDEBAR: Pilih News Feed / Features
#########################################
logo_path = "cat_logo.webp"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)

st.sidebar.header("Navigation")
section = st.sidebar.radio("Menu:", ["News Feed", "Features"])

#################################
# 5) BAGIAN HEAD & CRYPTO CARDS
#################################
st.title("🚀 Realtime Macro & Crypto Dashboard")

# Tampilkan info refresh
st.markdown("**Data refreshes automatically every 15 seconds.**")

# Inisialisasi
if 'crypto_prices' not in st.session_state:
    st.session_state.crypto_prices = get_crypto_prices()
if 'last_price_refresh' not in st.session_state:
    st.session_state.last_price_refresh = time.time()

if time.time() - st.session_state.last_price_refresh >= 15:
    st.session_state.crypto_prices = get_crypto_prices()
    st.session_state.last_price_refresh = time.time()

st.subheader("Live Crypto Prices")
col1, col2, col3 = st.columns(3)
cryptos = [("Bitcoin (BTC)", "bitcoin"),
           ("Ethereum (ETH)", "ethereum"),
           ("Solana (SOL)", "solana")]

for (name, key), c in zip(cryptos, [col1, col2, col3]):
    with c:
        d = st.session_state.crypto_prices.get(key, {})
        price = d.get("usd", 0)
        change = d.get("usd_24h_change", 0)
        change_class = "negative" if change < 0 else "positive"
        st.markdown(f"""
        <div class='crypto-card'>
            <h3 class='crypto-name {key}'>{name}</h3>
            <p class='crypto-price'>${price:,.2f}</p>
            <p class='crypto-change {change_class}'>{change:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

# Pemisah
st.write("---")

########################################
# 6) MAIN CONTENT: News Feed / Features
########################################
if section == "News Feed":
    # Row: (colA: jam) (colB: feed) (colC: cari)
    colA, colB, colC = st.columns([1,2,2])
    with colA:
        st.markdown(f"**Sekarang**:\n{show_utc_wib_time()}")

    with colB:
        feed_choice = st.selectbox("Pilih sumber berita:", list(NEWS_SOURCES.keys()))

    with colC:
        search_keyword = st.text_input("Cari Berita:")

    st.subheader("📰 Berita Terbaru")

    if feed_choice == "NEWEST":
        feeds = RSS_FEEDS["NEWEST"]
        all_news = []
        for f_url in feeds:
            all_news.extend(fetch_news(f_url, max_entries=3))
    else:
        f_url = NEWS_SOURCES[feed_choice]
        all_news = fetch_news(f_url, max_entries=10)

    # Sort by published time
    all_news.sort(key=lambda x: x["published_time"], reverse=True)

    # Filter by keyword
    if search_keyword:
        all_news = [n for n in all_news if search_keyword.lower() in n["title"].lower()]

    display_news_items(all_news)

elif section == "Features":
    st.subheader("Fitur Tambahan")
    # Fitur: Fear & Greed / Rainbow
    feature_choice = st.selectbox("Pilih Fitur:", FEATURES)

    if feature_choice == "Fear and Greed Index":
        st.markdown("### Fear and Greed Index")
        st.warning("Iframe is blocked by the site. Click the link below to view.")
        st.markdown("[Visit Fear and Greed Index](https://alternative.me/crypto/fear-and-greed-index/)")

    elif feature_choice == "Bitcoin Rainbow Chart":
        st.markdown("### Bitcoin Rainbow Chart")
        st.warning("Iframe is blocked by the site. Click the link below to view.")
        st.markdown("[Visit Bitcoin Rainbow Chart](https://www.blockchaincenter.net/en/bitcoin-rainbow-chart/)")

    # Tambah chart BTC 30 hari
    st.markdown("### 📈 Bitcoin Price (30 Day Chart)")
    dts, prcs = get_bitcoin_history(30)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dts, y=prcs, name="BTC", line=dict(color='gold')))
    fig.update_layout(
        title="Harga Bitcoin - 30 Hari",
        xaxis_title="Tanggal",
        yaxis_title="USD",
        template="plotly_dark",
        paper_bgcolor="#1e1e2f",
        plot_bgcolor="#1e1e2f",
        font_color="white",
    )
    st.plotly_chart(fig, use_container_width=True)

# Auto-refresh
st_autorefresh(interval=15000, key="refresh-15s")
