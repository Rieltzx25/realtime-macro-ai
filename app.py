import streamlit as st
import feedparser
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os
import plotly.graph_objects as go
from textblob import TextBlob

#############################
# ALL-IN-ONE SINGLE-FILE UI #
#############################

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard 🚀", layout="wide")

# ==========================================
# ============ CUSTOM CSS ==================
# ==========================================
st.markdown(
    """
    <style>
    /* Global Background */
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a4a 100%);
        position: relative;
    }

    /* News Card */
    .news-card {
        background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border: 1px solid transparent;
        background-image: linear-gradient(#1a1a1a, #1a1a1a),
                          linear-gradient(45deg, #FF4500, #FFD700);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }
    .news-card:hover {
        box-shadow: 0 6px 12px rgba(255, 255, 255, 0.15);
        transform: translateY(-3px);
    }
    .news-headline {
        color: #FFFFFF;
        font-size: 20px;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    .news-summary {
        color: #CCCCCC;
        font-size: 14px;
    }
    .news-timestamp {
        color: #888;
        font-size: 12px;
    }

    /* Crypto Card */
    .crypto-card {
        background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border: 1px solid transparent;
        background-image: linear-gradient(#1a1a1a, #1a1a1a),
                          linear-gradient(45deg, #FFD700, #00FF00);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        transition: transform 0.2s ease-in-out;
    }
    .crypto-card:hover {
        transform: scale(1.02);
    }
    .crypto-name {
        font-size: 20px;
        font-weight: bold;
    }
    .crypto-name.bitcoin {
        color: #FFD700;
    }
    .crypto-name.ethereum, .crypto-name.solana {
        color: #FFFFFF;
    }
    .crypto-price {
        font-size: 18px;
        font-weight: bold;
        color: #FFFFFF;
    }
    .crypto-change {
        font-size: 16px;
    }
    .crypto-change.negative {
        color: #FF0000;
    }
    .crypto-change.positive {
        color: #00FF00;
    }

    /* Sidebar */
    .stSidebar {
        background: linear-gradient(180deg, #2a2a4a 0%, #1e1e2f 100%);
        border-right: 1px solid #FFD700;
    }
    h1 {
        color: #FFD700 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    h2 {
        color: #00FF00 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }

    /* Sidebar Clock Container */
    .sidebar-clock-container {
        background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
        padding: 10px 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border: 1px solid transparent;
        background-image: linear-gradient(#1a1a1a, #1a1a1a),
                          linear-gradient(45deg, #00FF00, #FFD700);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        color: #FFFFFF;
        font-size: 14px;
        margin-top: 20px;
    }
    .clock-text {
        margin: 2px 0;
        color: #CCCCCC;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

########################################################
# BAGIAN PENTING: TETAPKAN RSS_FEEDS, NEWS_SOURCES, dll #
########################################################
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

##################################
# FUNGSI TAMBAHAN & UTILITAS LAIN #
##################################
def display_sidebar_clock():
    """Menampilkan jam UTC & WIB di Sidebar, tanpa tampilan mencolok."""
    now = datetime.utcnow()
    utc_time_str = now.strftime("%H:%M:%S") + " UTC"

    # WIB (UTC+7)
    wib_offset = 7
    wib_time = (now.hour + wib_offset) % 24
    # jam:menit:detik
    wib_time_str = f"{wib_time:02d}:{now.minute:02d}:{now.second:02d} WIB"

    st.sidebar.markdown(
        f"""
        <div class="sidebar-clock-container">
            <div class="clock-text">UTC   : {utc_time_str}</div>
            <div class="clock-text">WIB   : {wib_time_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    except Exception:
        return []

def get_crypto_prices():
    prices = {"bitcoin": {}, "ethereum": {}, "solana": {}}
    url = ("https://api.coingecko.com/api/v3/simple/price"
           "?ids=bitcoin,ethereum,solana"
           "&vs_currencies=usd"
           "&include_24hr_change=true")
    try:
        r = requests.get(url, timeout=5).json()
        for coin in prices:
            if coin in r:
                prices[coin] = {
                    "usd": r[coin].get("usd", 0),
                    "usd_24h_change": r[coin].get("usd_24h_change", 0)
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

from textblob import TextBlob

def analyze_sentiment(text):
    try:
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0:
            return 'Positif'
        elif analysis.sentiment.polarity < 0:
            return 'Negatif'
        else:
            return 'Netral'
    except:
        return 'Tidak Diketahui'

def display_news_items(news_list):
    """Menampilkan kartu berita + SENTIMEN: ..."""
    if not news_list:
        st.write("Tidak ada berita.")
        return
    for item in news_list:
        dt_item = datetime.fromtimestamp(item["published_time"])
        sentiment_result = analyze_sentiment(item['summary'])
        st.markdown(f"""
        <div class='news-card'>
            <p class='news-headline'>{item['title']}</p>
            <p class='news-timestamp'>
                {dt_item.strftime("%a, %d %b %Y %H:%M:%S UTC")} 
                | <strong>SENTIMEN: {sentiment_result}</strong>
            </p>
            <p class='news-summary'>{item['summary']}</p>
            <p><a href='{item['link']}' target='_blank'>🔗 Baca Selengkapnya</a></p>
        </div>
        """, unsafe_allow_html=True)

##########################
# SIDEBAR DAN NAVIGASI  #
##########################
logo_path = "cat_logo.webp"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)

st.sidebar.header("Navigation")
section = st.sidebar.radio("Choose Section", ["News Feed", "Features"])

# Input untuk cari berita
search_keyword = st.sidebar.text_input("🔍 Cari Berita:")

# Tampilkan jam di sidebar (lebih minimalis)
display_sidebar_clock()

#################################
# HEADER & LIVE CRYPTO PRICES  #
#################################
st.title("🚀 Realtime Macro & Crypto Dashboard")
st.subheader("Live Crypto Prices")

# Inisialisasi data harga crypto
if 'crypto_prices' not in st.session_state:
    st.session_state.crypto_prices = get_crypto_prices()
if 'last_price_refresh' not in st.session_state:
    st.session_state.last_price_refresh = time.time()

# Update harga tiap 15 detik
if time.time() - st.session_state.last_price_refresh >= 15:
    st.session_state.crypto_prices = get_crypto_prices()
    st.session_state.last_price_refresh = time.time()

# Tampilkan 3 crypto (BTC, ETH, SOL)
col1, col2, col3 = st.columns(3)
cryptos = [
    ("Bitcoin (BTC)", "bitcoin"),
    ("Ethereum (ETH)", "ethereum"),
    ("Solana (SOL)", "solana")
]
for col, (name, key) in zip([col1, col2, col3], cryptos):
    with col:
        data = st.session_state.crypto_prices.get(key, {})
        price = data.get("usd", 0)
        change = data.get("usd_24h_change", 0)
        change_class = 'negative' if change < 0 else 'positive'
        st.markdown(f"""
        <div class='crypto-card'>
            <h3 class='crypto-name {key}'>{name}</h3>
            <p class='crypto-price'>${price:,.2f}</p>
            <p class='crypto-change {change_class}'>{change:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

st.info("🔄 Data refreshes automatically every 15 seconds.")

########################
# BAGIAN UTAMA (CONTENT)
########################
if section == "News Feed":
    st.subheader("📰 Berita Terbaru")

    # Pilih sumber berita di sidebar
    feed_choice = st.sidebar.selectbox("Pilih sumber berita", list(NEWS_SOURCES.keys()))

    if feed_choice == "NEWEST":
        feeds = RSS_FEEDS["NEWEST"]
        all_news = []
        for feed in feeds:
            all_news.extend(fetch_news(feed, max_entries=3))
    else:
        feed_url = NEWS_SOURCES[feed_choice]
        all_news = fetch_news(feed_url, max_entries=10)

    # Urutkan berita berdasarkan waktu publish
    all_news.sort(key=lambda x: x["published_time"], reverse=True)

    # Filter berita berdasarkan keyword
    if search_keyword:
        all_news = [n for n in all_news if search_keyword.lower() in n["title"].lower()]

    # Tampilkan berita + sentiment
    display_news_items(all_news)

elif section == "Features":
    # Pilih fitur
    feature_choice = st.sidebar.selectbox("Pilih fitur", FEATURES)

    if feature_choice == "Fear and Greed Index":
        st.subheader("Fear and Greed Index")
        st.warning("Iframe is blocked by the site. Click the link below to view.")
        st.markdown("[Visit Fear and Greed Index](https://alternative.me/crypto/fear-and-greed-index/)")

    elif feature_choice == "Bitcoin Rainbow Chart":
        st.subheader("Bitcoin Rainbow Chart")
        st.warning("Iframe is blocked by the site. Click the link below to view.")
        st.markdown("[Visit Bitcoin Rainbow Chart](https://www.blockchaincenter.net/en/bitcoin-rainbow-chart/)")

    # Contoh tambahan: Tampilkan grafik BTC 30 hari
    st.subheader("📈 Bitcoin Price (30 Day Chart)")
    dates, prices = get_bitcoin_history(30)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prices, name="BTC", line=dict(color='gold')))
    # Ubah layout mirip dark theme
    fig.update_layout(
        title="Harga Bitcoin - 30 Hari",
        xaxis_title="Tanggal",
        yaxis_title="USD",
        template="plotly_dark",  # tema gelap
        paper_bgcolor="#1e1e2f",
        plot_bgcolor="#1e1e2f",
        font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

# Auto-refresh the entire app setiap 15 detik
st_autorefresh(interval=15000, key="refresh")
