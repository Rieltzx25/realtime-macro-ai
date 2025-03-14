import streamlit as st
import feedparser
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Konfigurasi Halaman
st.set_page_config(
    page_title="Realtime Macro & Crypto Dashboard 🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Kustom untuk Styling
st.markdown("""
    <style>
    .main {
        background-color: #1e1e2f;
    }
    .card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .headline {
        color: #4169E1;
    }
    .positive {
        color: #00FF00;
    }
    .negative {
        color: #FF0000;
    }
    </style>
""", unsafe_allow_html=True)

# Fungsi untuk Mengambil Berita
def fetch_news(url, max_entries=5):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if resp.status_code != 200:
        return []
    feed = feedparser.parse(resp.text)
    news_data = []
    for entry in feed.entries[:max_entries]:
        published_time = time.mktime(entry.published_parsed) if hasattr(entry, "published_parsed") else 0
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') and len(entry.summary) > 300 else entry.summary
        news_data.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "published_time": published_time
        })
    return news_data

# Fungsi untuk Mengambil Harga Crypto
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
        st.error(f"Gagal mengambil harga crypto: {e}")
        return None
    return prices

# Daftar RSS Feed
RSS_FEEDS = {
    "Newest": [
        "https://www.cnbc.com/id/20910258/device/rss/rss.html",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "https://www.reutersagency.com/feed/?best-topics=business-finance",
        "https://www.reutersagency.com/feed/?best-topics=markets",
        "https://www.investing.com/rss/news_14.rss",
        "https://www.investing.com/rss/news_301.rss",
        "https://feeds.marketwatch.com/marketwatch/topstories/",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://finance.yahoo.com/news/rssindex",
        "https://coinvestasi.com/feed"
    ]
}

# Menu Sidebar
section = st.sidebar.radio("Dashboard Menu", ["News Feed", "Crypto Prices", "Features"])

# Konten Utama
st.title("🚀 Realtime Macro & Crypto Dashboard")

if section == "News Feed":
    feed_choice = st.sidebar.selectbox("Pilih Sumber Berita", list(RSS_FEEDS.keys()))
    all_news = []
    for feed_url in RSS_FEEDS[feed_choice]:
        all_news.extend(fetch_news(feed_url, max_entries=3))
    all_news.sort(key=lambda x: x["published_time"], reverse=True)

    st.subheader(f"🔥 Berita {feed_choice}")
    if not all_news:
        st.write("Tidak ada berita tersedia.")
    else:
        for item in all_news[:10]:
            dt_item = datetime.fromtimestamp(item["published_time"])
            news_html = f"""
            <div class='card'>
                <h3 class='headline'>{item['title']}</h3>
                <p style='color: #888; font-size: 0.8em;'>{dt_item.strftime("%a, %d %b %Y %H:%M:%S UTC")}</p>
                <p>{item['summary']}</p>
                <a href='{item['link']}' target='_blank'>Baca Selengkapnya</a>
            </div>
            """
            st.markdown(news_html, unsafe_allow_html=True)

elif section == "Crypto Prices":
    st.subheader("Harga Crypto Live")
    crypto_prices = get_crypto_prices()
    if crypto_prices:
        col1, col2, col3 = st.columns(3)
        cryptos = [("Bitcoin (BTC)", "bitcoin"), ("Ethereum (ETH)", "ethereum"), ("Solana (SOL)", "solana")]
        for col, (name, key) in zip([col1, col2, col3], cryptos):
            with col:
                price = crypto_prices[key]['usd']
                change = crypto_prices[key]['usd_24h_change']
                change_class = 'positive' if change > 0 else 'negative'
                st.markdown(f"""
                <div class='card'>
                    <h3>{name}</h3>
                    <p>Harga: ${price:,.2f}</p>
                    <p>Perubahan 24h: <span class='{change_class}'>{change:.2f}%</span></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.write("Tidak dapat memuat harga crypto.")

elif section == "Features":
    st.subheader("Fitur Tambahan")
    st.write("Fitur tambahan seperti Fear and Greed Index atau Bitcoin Rainbow Chart dapat ditambahkan di sini.")

# Auto-refresh setiap 15 detik
st_autorefresh(interval=15_000, limit=None, key="dashboard_refresher")
