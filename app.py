import streamlit as st
import feedparser
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os

st.set_page_config(page_title="Realtime Macro & Crypto Dashboard 🚀", layout="wide")

# Add custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #1e1e2f;
    }
    .news-card {
        background-color: #000000;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .news-headline {
        color: #FFFFFF;
        font-size: 20px;
        font-weight: bold;
    }
    .news-summary {
        color: #CCCCCC;
        font-size: 14px;
    }
    .news-timestamp {
        color: #888;
        font-size: 12px;
    }
    .crypto-card {
    background-color: #000000;
    padding: 15px;
    border-radius: 20px; /* Sudut lebih bulat */
    text-align: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Shadow lebih lembut */
    border: 1px solid transparent; /* Untuk gradient border */
    background-image: linear-gradient(#000000, #000000), 
                      linear-gradient(45deg, #FFD700, #00FF00); /* Gradient border */
    background-origin: border-box;
    background-clip: padding-box, border-box;
    transition: transform 0.2s ease-in-out; /* Efek hover */
}
.crypto-card:hover {
    transform: scale(1.02); /* Efek zoom saat hover */
}
.news-card {
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.news-card:hover {
    box-shadow: 0 4px 10px rgba(255, 255, 255, 0.1);
    transform: translateY(-3px);

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
    </style>
""", unsafe_allow_html=True)

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
# Fungsi ambil harga crypto dengan debugging untuk perubahan harian
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
# Sidebar: Pilih Section dengan Logo
# --------------------------------------
# Cek apakah file cat.logo.webp ada
logo_path = "cat_logo.webp"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=False, width=150)
else:
    st.sidebar.error(f"File {logo_path} tidak ditemukan. Pastikan file ada di direktori utama repositori.")

st.sidebar.header("Navigation")
section = st.sidebar.radio("Choose Section", ["News Feed", "Features"])

if section == "News Feed":
    feed_choice = st.sidebar.selectbox("Pilih sumber berita", list(NEWS_SOURCES.keys()))
elif section == "Features":
    feature_choice = st.sidebar.selectbox("Pilih fitur", FEATURES)

# --------------------------------------
# Title
# --------------------------------------
st.title("🚀 Realtime Macro & Crypto Dashboard")

# Harga Crypto with automatic refresh
st.subheader("Live Crypto Prices")
col1, col2, col3 = st.columns(3)
cryptos = [
    ("Bitcoin (BTC)", "bitcoin"),
    ("Ethereum (ETH)", "ethereum"),
    ("Solana (SOL)", "solana")
]
for col, (name, key) in zip([col1, col2, col3], cryptos):
    with col:
        price = st.session_state.crypto_prices[key]['usd']
        change = st.session_state.crypto_prices[key]['usd_24h_change']
        change_class = 'negative' if change < 0 else 'positive'
        name_class = 'bitcoin' if 'Bitcoin' in name else ('ethereum' if 'Ethereum' in name else 'solana')
        st.markdown(f"""
        <div class='crypto-card'>
            <h3 class='crypto-name {name_class}'>{name}</h3>
            <p class='crypto-price'>${price:,.2f}</p>
            <p class='crypto-change {change_class}'>{change:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

st.info("🔄 Data refreshes automatically every 15 seconds.")

# Fungsi tampil berita
def display_news_items(news_list):
    if not news_list:
        st.write("Tidak ada berita.")
        return
    top_news = news_list[0]
    dt_top = datetime.fromtimestamp(top_news["published_time"])
    news_html = f"""
    <div class='news-card'>
        <h3 class='news-headline'>{top_news['title']}</h3>
        <p class='news-timestamp'>{dt_top.strftime("%a, %d %b %Y %H:%M:%S UTC")}</p>
        <p class='news-summary'>{top_news['summary']}</p>
        <p><a href='{top_news['link']}' target='_blank'>Baca selengkapnya</a></p>
    </div>
    """
    st.markdown(news_html, unsafe_allow_html=True)
    st.markdown("---")
    for item in news_list[1:10]:
        dt_item = datetime.fromtimestamp(item["published_time"])
        item_html = f"""
        <div class='news-card'>
            <p class='news-headline'>{item['title']}</p>
            <p class='news-timestamp'>{dt_item.strftime("%a, %d %b %Y %H:%M:%S UTC")}</p>
            <p class='news-summary'>{item['summary']}</p>
            <p><a href='{item['link']}' target='_blank'>Link</a></p>
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
    st.subheader(f"🔥 Berita Terbaru - {feed_choice}")
    display_news_items(all_news)
elif section == "Features":
    if feature_choice == "Fear and Greed Index":
        st.subheader("Fear and Greed Index")
        st.warning("Iframe is blocked by the site. Click the link below to view.")
        st.link_button("Visit Fear and Greed Index", "https://alternative.me/crypto/fear-and-greed-index/")
    elif feature_choice == "Bitcoin Rainbow Chart":
        st.subheader("Bitcoin Rainbow Chart")
        st.warning("Iframe is blocked by the site. Click the link below to view.")
        st.link_button("Visit Bitcoin Rainbow Chart", "https://www.blockchaincenter.net/en/bitcoin-rainbow-chart/")

# Auto-refresh the entire app every 15 seconds
st_autorefresh(interval=15_000, limit=None, key="price_refresher")
