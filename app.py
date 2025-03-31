import streamlit as st
import feedparser
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os

# Configure Streamlit page settings
st.set_page_config(
    page_title="Crypto Terminal Pro 📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/crypto-terminal',
        'Report a bug': "https://github.com/yourusername/crypto-terminal/issues",
        'About': "# Crypto Terminal Pro\nA professional-grade cryptocurrency dashboard with real-time data and news."
    }
)

# Add custom CSS for improved styling
st.markdown("""
    <style>
    /* Color Palette */
    :root {
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --accent-primary: #22c55e;
        --accent-secondary: #10b981;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --up-color: #22c55e;
        --down-color: #ef4444;
        --hover-color: #334155;
        --border-color: #475569;
    }
    
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');
    
    /* Main container styling */
    .main {
        background-color: var(--bg-dark);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }
    
    /* Terminal header */
    .terminal-header {
        background: linear-gradient(90deg, var(--bg-dark) 0%, var(--bg-card) 100%);
        border-bottom: 1px solid var(--border-color);
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 8px;
    }
    
    /* Card styling */
    .bloomberg-card {
        background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-card) 100%);
        border: 1px solid var(--border-color);
        padding: 20px;
        margin-bottom: 15px;
        font-family: 'IBM Plex Mono', monospace;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .bloomberg-card:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
        border-color: var(--accent-primary);
    }
    
    /* Clock styling */
    .clock-container {
        background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-card) 100%);
        border: 1px solid var(--border-color);
        padding: 15px;
        border-radius: 8px;
        font-family: 'IBM Plex Mono', monospace;
        margin: 10px 0;
        color: var(--text-primary);
    }
    
    .clock-text {
        font-size: 14px;
        line-height: 1.5;
        color: var(--text-secondary);
    }
    
    .clock-date {
        color: var(--accent-primary);
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .clock-time {
        color: var(--accent-secondary);
        font-size: 16px;
        font-weight: 600;
    }
    
    /* Crypto price cards */
    .bloomberg-crypto {
        background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-card) 100%);
        border: 1px solid var(--border-color);
        padding: 20px;
        text-align: center;
        font-family: 'IBM Plex Mono', monospace;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .bloomberg-crypto:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
        border-color: var(--accent-primary);
    }
    
    .crypto-name {
        color: var(--text-primary);
        font-size: 18px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }
    
    .crypto-price {
        color: var(--accent-primary);
        font-size: 24px;
        font-weight: 600;
        margin: 15px 0;
    }
    
    .crypto-change {
        font-size: 16px;
        font-weight: 500;
        padding: 5px 10px;
        border-radius: 5px;
        display: inline-block;
    }
    
    .crypto-change.positive {
        color: var(--up-color);
        background: rgba(34, 197, 94, 0.1);
    }
    
    .crypto-change.negative {
        color: var(--down-color);
        background: rgba(239, 68, 68, 0.1);
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: #0a0a0f;
        border-right: 1px solid #00ff00;
        padding: 20px;
    }
    
    /* Titles */
    h1 {
        color: #00ff00 !important;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 20px !important;
    }
    
    h2 {
        color: #00ff00 !important;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 20px 0 !important;
    }
    
    /* Links */
    a {
        color: #00ff00;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: #7fff7f;
        text-decoration: none;
    }
    
    /* Info and warning boxes */
    .stInfo {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid #00ff00;
        color: #00ff00;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .stWarning {
        background: rgba(255, 68, 68, 0.1);
        border: 1px solid #ff4444;
        color: #ff4444;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #00ff00 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #0a0a0f;
        color: #00ff00;
        border: 1px solid #00ff00;
        padding: 10px 20px;
        border-radius: 5px;
        font-family: 'IBM Plex Mono', monospace;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #00ff00;
        color: #0a0a0f;
    }
    
    /* Search box */
    .stTextInput > div > div > input {
        background-color: #0a0a0f;
        color: #00ff00;
        border: 1px solid #00ff00;
        padding: 10px;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        background-color: #0a0a0f;
        color: #00ff00;
        text-align: center;
        padding: 5px 10px;
        border-radius: 3px;
        border: 1px solid #00ff00;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
""", unsafe_allow_html=True)

# Display welcome message and help
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True

if st.session_state.show_welcome:
    st.info("""
    👋 Welcome to Crypto Terminal Pro!
    
    This dashboard provides real-time cryptocurrency prices and news updates.
    
    - 📈 View live crypto prices
    - 📰 Read latest news from multiple sources
    - 📊 Access market analysis tools
    - ⚡ Auto-refreshes every 15 seconds
    
    Click the X in the top right to dismiss this message.
    """)
    if st.button("Don't show this again"):
        st.session_state.show_welcome = False
        st.rerun()

# --------------------------------------
# Fungsi untuk menampilkan jam menggunakan JavaScript
# --------------------------------------
def display_clock(container="clock"):
    clock_html = f"""
    <div class='clock-container' id='{container}'>
        <div class='clock-text clock-date' id='date-{container}'></div>
        <div class='clock-text clock-time' id='utc-{container}'></div>
        <div class='clock-text clock-time' id='wib-{container}'></div>
    </div>
    <script>
    function updateClock_{container}() {{
        const now = new Date();
        // UTC time
        const utc = now.toUTCString().split(' ')[4] + ' UTC';
        // WIB time (UTC+7)
        const wibOffset = 7 * 60 * 60 * 1000;
        const wib = new Date(now.getTime() + wibOffset);
        const wibStr = wib.toISOString().substr(11, 8) + ' WIB';
        // Tanggal
        const dateStr = now.toLocaleDateString('en-US', {{ 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        }});
        
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
st.title("🚀 CRYPTO TERMINAL PRO")

# Update the crypto display section
display_crypto_prices()

# --------------------------------------
# Fungsi tampil berita
# --------------------------------------
def display_news_items(news_list):
    if not news_list:
        st.warning("⚠️ No news available at the moment. Please try another source or check back later.")
        return
        
    # Filter news if search term exists
    if search_term:
        news_list = [
            news for news in news_list 
            if search_term.lower() in news['title'].lower() 
            or search_term.lower() in news['summary'].lower()
        ]
        
    if not news_list:
        st.warning(f"No news found matching '{search_term}'")
        return
        
    with st.spinner('Loading latest news...'):
        for item in news_list:
            dt_item = datetime.fromtimestamp(item["published_time"])
            st.markdown(f"""
            <div class='bloomberg-card'>
                <div class='bloomberg-headline'>{item['title']}</div>
                <div class='bloomberg-timestamp'>
                    <span class="tooltip">
                        {dt_item.strftime("%Y-%m-%d %H:%M:%S UTC")}
                        <span class="tooltiptext">Published time in UTC</span>
                    </span>
                </div>
                <div class='bloomberg-text'>{item['summary']}</div>
                <div><a href='{item['link']}' target='_blank'>🔗 READ FULL ARTICLE</a></div>
            </div>
            """, unsafe_allow_html=True)

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

# Add search functionality for news
st.sidebar.markdown("### 🔍 Search News")
search_term = st.sidebar.text_input("Enter keywords to filter news", "")

# Add help text for features
with st.sidebar.expander("ℹ️ How to Use"):
    st.markdown("""
    **Quick Guide:**
    1. Use the navigation radio buttons to switch between News and Features
    2. Select news sources from the dropdown menu
    3. Use the search box to filter news by keywords
    4. Click on news headlines to read full articles
    5. Watch the auto-updating crypto prices
    """)

# Add market summary
with st.sidebar.expander("📊 Market Summary"):
    st.markdown("""
    **24h Market Overview:**
    - Total Market Cap: $2.34T
    - 24h Volume: $98.2B
    - BTC Dominance: 52.3%
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7fff7f; font-size: 12px;'>
    Made with 💚 by Your Name | Data provided by CoinGecko and various news sources
</div>
""", unsafe_allow_html=True) 
