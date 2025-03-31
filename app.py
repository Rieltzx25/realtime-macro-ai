import streamlit as st
import feedparser
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os

st.set_page_config(page_title="Bloomberg-Style Terminal 📊", layout="wide")

# Add custom CSS for Bloomberg Terminal-like styling
st.markdown("""
    <style>
    /* Import Bloomberg Terminal-like font */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    
    .main {
        background-color: #000000;
        color: #00ff00;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    /* Terminal-like header */
    .terminal-header {
        background: #000000;
        border-bottom: 1px solid #00ff00;
        padding: 10px;
        margin-bottom: 20px;
    }
    
    /* Bloomberg-style cards */
    .bloomberg-card {
        background: #000000;
        border: 1px solid #00ff00;
        padding: 15px;
        margin-bottom: 10px;
        font-family: 'IBM Plex Mono', monospace;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.1);
    }
    
    .bloomberg-card:hover {
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
    }
    
    /* Bloomberg-style headlines */
    .bloomberg-headline {
        color: #00ff00;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Bloomberg-style text */
    .bloomberg-text {
        color: #00ff00;
        font-size: 14px;
        line-height: 1.4;
    }
    
    /* Bloomberg-style timestamp */
    .bloomberg-timestamp {
        color: #00ff00;
        font-size: 12px;
        opacity: 0.7;
    }
    
    /* Bloomberg-style crypto cards */
    .bloomberg-crypto {
        background: #000000;
        border: 1px solid #00ff00;
        padding: 15px;
        text-align: center;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    .bloomberg-crypto:hover {
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
    }
    
    .crypto-name {
        font-size: 16px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .crypto-price {
        font-size: 20px;
        font-weight: 600;
        margin: 10px 0;
    }
    
    .crypto-change {
        font-size: 14px;
        font-weight: 500;
    }
    
    .crypto-change.positive {
        color: #00ff00;
    }
    
    .crypto-change.negative {
        color: #ff0000;
    }
    
    /* Bloomberg-style sidebar */
    .stSidebar {
        background-color: #000000;
        border-right: 1px solid #00ff00;
    }
    
    /* Bloomberg-style titles */
    h1 {
        color: #00ff00 !important;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    h2 {
        color: #00ff00 !important;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Bloomberg-style clock */
    .bloomberg-clock {
        background: #000000;
        border: 1px solid #00ff00;
        padding: 10px;
        font-family: 'IBM Plex Mono', monospace;
        color: #00ff00;
        font-size: 12px;
    }
    
    /* Bloomberg-style links */
    a {
        color: #00ff00;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    /* Bloomberg-style info box */
    .stInfo {
        background: #000000;
        border: 1px solid #00ff00;
        color: #00ff00;
        padding: 10px;
        border-radius: 0;
    }
    
    /* Bloomberg-style warning box */
    .stWarning {
        background: #000000;
        border: 1px solid #ff0000;
        color: #ff0000;
        padding: 10px;
        border-radius: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------
# Fungsi untuk menampilkan jam menggunakan JavaScript
# --------------------------------------
def display_clock(container="clock"):
    clock_html = f"""
    <div class='{container}' id='{container}'>
        <div class='clock-text' id='date-{container}'></div>
        <div class='clock-text' id='utc-{container}'></div>
        <div class='clock-text' id='wib-{container}'></div>
    </div>
    <script>
    function updateClock_{container}() {{
        const now = new Date();
        // UTC time
        const utc = now.toUTCString().split(' ')[4] + ' UTC';
        // WIB time (UTC+7)
        const wibOffset = 7 * 60 * 60 * 1000; // 7 jam dalam milidetik
        const wib = new Date(now.getTime() + wibOffset);
        const wibStr = wib.toISOString().substr(11, 8) + ' WIB';
        // Tanggal
        const dateStr = now.toUTCString().split(' ').slice(0, 4).join(' ');
        
        document.getElementById('date-{container}').innerText = dateStr;
        document.getElementById('utc-{container}').innerText = utc;
        document.getElementById('wib-{container}').innerText = wibStr;
    }}
    updateClock_{container}();
    setInterval(updateClock_{container}, 1000);
    </script>
    """
    return clock_html

# --------------------------------------
# Fungsi ambil berita dari RSS (User-Agent)
# --------------------------------------
def fetch_news(url, max_entries=5):
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)

        news_data = []
        for entry in feed.entries[:max_entries]:
            published_time = time.mktime(entry.published_parsed) if hasattr(entry, "published_parsed") else 0
            summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') and entry.summary else "No summary available."
            news_data.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summary,
                "published_time": published_time
            })
        return news_data
    except requests.exceptions.RequestException as e:
        print(f"RSS fetch error: {url} - {e}")
        return []

# --------------------------------------
# Fungsi ambil harga crypto
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

# Initialize session state for crypto prices and last refresh time
if 'crypto_prices' not in st.session_state:
    st.session_state.crypto_prices = get_crypto_prices()
if 'last_price_refresh' not in st.session_state:
    st.session_state.last_price_refresh = time.time()

# Check if 15 seconds have passed since the last refresh
current_time = time.time()
if current_time - st.session_state.last_price_refresh >= 15:
    st.session_state.crypto_prices = get_crypto_prices()
    st.session_state.last_price_refresh = current_time

# --------------------------------------
# Daftar RSS Feeds dan Features
# --------------------------------------
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

# --------------------------------------
# Sidebar: Pilih Section dengan Logo dan Jam
# --------------------------------------
logo_path = "cat_logo.webp"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=False, width=150)
else:
    st.sidebar.error(f"File {logo_path} tidak ditemukan. Pastikan file ada di direktori utama repositori.")

st.sidebar.header("NAVIGATION")
section = st.sidebar.radio("CHOOSE SECTION", ["News Feed", "Features"])

if section == "News Feed":
    feed_choice = st.sidebar.selectbox("SELECT NEWS SOURCE", list(NEWS_SOURCES.keys()))
elif section == "Features":
    feature_choice = st.sidebar.selectbox("SELECT FEATURE", FEATURES)

# Tambahkan jam di sidebar
st.sidebar.markdown(display_clock(container="sidebar-clock"), unsafe_allow_html=True)

# --------------------------------------
# Title
# --------------------------------------
st.title("🚀 BLOOMBERG-STYLE CRYPTO TERMINAL")

# Update the crypto display section
st.markdown("""
    <div class='terminal-header'>
        <div class='bloomberg-headline'>LIVE CRYPTO PRICES</div>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
cryptos = [
    ("BITCOIN (BTC)", "bitcoin"),
    ("ETHEREUM (ETH)", "ethereum"),
    ("SOLANA (SOL)", "solana")
]
for col, (name, key) in zip([col1, col2, col3], cryptos):
    with col:
        price = st.session_state.crypto_prices[key]['usd']
        change = st.session_state.crypto_prices[key]['usd_24h_change']
        change_class = 'negative' if change < 0 else 'positive'
        st.markdown(f"""
        <div class='bloomberg-crypto'>
            <div class='crypto-name'>{name}</div>
            <div class='crypto-price'>${price:,.2f}</div>
            <div class='crypto-change {change_class}'>{change:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
    <div class='bloomberg-text' style='text-align: center; margin: 10px 0;'>
        DATA REFRESHES EVERY 15 SECONDS
    </div>
""", unsafe_allow_html=True)

# --------------------------------------
# Fungsi tampil berita
# --------------------------------------
def display_news_items(news_list):
    if not news_list:
        st.write("NO NEWS AVAILABLE")
        return
    top_news = news_list[0]
    dt_top = datetime.fromtimestamp(top_news["published_time"])
    news_html = f"""
    <div class='bloomberg-card'>
        <div class='bloomberg-headline'>{top_news['title']}</div>
        <div class='bloomberg-timestamp'>{dt_top.strftime("%Y-%m-%d %H:%M:%S UTC")}</div>
        <div class='bloomberg-text'>{top_news['summary']}</div>
        <div><a href='{top_news['link']}' target='_blank'>READ MORE</a></div>
    </div>
    """
    st.markdown(news_html, unsafe_allow_html=True)
    st.markdown("---")
    for item in news_list[1:10]:
        dt_item = datetime.fromtimestamp(item["published_time"])
        item_html = f"""
        <div class='bloomberg-card'>
            <div class='bloomberg-headline'>{item['title']}</div>
            <div class='bloomberg-timestamp'>{dt_item.strftime("%Y-%m-%d %H:%M:%S UTC")}</div>
            <div class='bloomberg-text'>{item['summary']}</div>
            <div><a href='{item['link']}' target='_blank'>READ MORE</a></div>
        </div>
        """
        st.markdown(item_html, unsafe_allow_html=True)

# --------------------------------------
# Tampilkan konten berdasar section
# --------------------------------------
if section == "News Feed":
    if feed_choice == "NEWEST":
        all_news = []
        for feed_url in NEWS_SOURCES["NEWEST"]:
            all_news.extend(fetch_news(feed_url, max_entries=3))
        all_news.sort(key=lambda x: x["published_time"], reverse=True)
    else:
        feed_url = NEWS_SOURCES[feed_choice]
        all_news = fetch_news(feed_url, max_entries=10)
        all_news.sort(key=lambda x: x["published_time"], reverse=True)
    st.subheader(f"🔥 LATEST NEWS - {feed_choice}")
    display_news_items(all_news)
elif section == "Features":
    if feature_choice == "Fear and Greed Index":
        st.subheader("FEAR AND GREED INDEX")
        st.warning("Iframe is blocked by the site. Click the link below to view.")
        st.link_button("VISIT FEAR AND GREED INDEX", "https://alternative.me/crypto/fear-and-greed-index/")
    elif feature_choice == "Bitcoin Rainbow Chart":
        st.subheader("BITCOIN RAINBOW CHART")
        st.warning("Iframe is blocked by the site. Click the link below to view.")
        st.link_button("VISIT BITCOIN RAINBOW CHART", "https://www.blockchaincenter.net/en/bitcoin-rainbow-chart/")

# --------------------------------------
# Tampilkan jam di ujung kiri bawah
# --------------------------------------
st.markdown(display_clock(container="clock"), unsafe_allow_html=True)

# Auto-refresh the entire app every 15 seconds
st_autorefresh(interval=15_000, limit=None, key="price_refresher") 
