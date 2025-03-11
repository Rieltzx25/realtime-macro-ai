import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import time

st.set_page_config(
    page_title="Realtime Macro & Crypto Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS custom
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stMarkdown h2, .stMarkdown h1 {
        color: #00FFA3;
    }
    .news-box {
        background-color: #1E222B;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .news-box:hover {
        background-color: #2E3440;
    }
    a {
        text-decoration: none;
        color: #00AFF0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Realtime Macro & Crypto Dashboard")

RSS_FEEDS = {
    "CNBC Economy": "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "Investing Crypto": "https://www.investing.com/rss/news_301.rss",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
    "CryptoSlate": "https://cryptoslate.com/feed/",
    "Bloomberg Markets": "https://www.bloomberg.com/feed/podcast/markets.xml",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/",
    "NewsBTC": "https://www.newsbtc.com/feed/",
    "CryptoPotato": "https://cryptopotato.com/feed/",
    "The Block": "https://www.theblock.co/rss.xml"
}

# Sidebar
with st.sidebar:
    st.header("⚙️ Options")
    feed_choice = st.selectbox("Pilih sumber berita", options=list(RSS_FEEDS.keys()))
    st.info("Data diperbarui otomatis setiap 30 detik")

@st.cache_data(ttl=30)
def fetch_feed(url):
    return feedparser.parse(url)

@st.cache_data
def get_summary(url):
    article = requests.get(url)
    soup = BeautifulSoup(article.content, "html.parser")
    paragraphs = soup.find_all('p')
    text = " ".join(p.get_text() for p in paragraphs)
    blob = TextBlob(text)
    sentences = blob.sentences
    return " ".join(str(sentence) for sentence in sentences[:3])

# Fetch news
feed = fetch_feed(RSS_FEEDS[feed_choice])

col1, col2 = st.columns([3, 1])

# News Headlines
with col1:
    st.header(f"📰 Berita Terkini - {feed_choice}")

    for entry in feed.entries[:10]:
        with st.expander(entry.title):
            st.markdown("<div class='news-box'>", unsafe_allow_html=True)
            with st.spinner('Generating summary...'):
                try:
                    summary = get_summary(entry.link)
                    st.write(summary)
                    st.markdown(f"[Baca lengkap disini]({entry.link})")
                except:
                    st.warning("Ringkasan tidak tersedia.")
                    st.markdown(f"[Baca lengkap disini]({entry.link})")
            st.markdown("</div>", unsafe_allow_html=True)

# Crypto Prices
with col2:
    st.header("📈 Live Crypto Prices")

    cryptos = ["bitcoin", "ethereum", "solana"]

    @st.cache_data(ttl=15)
    def get_crypto_prices():
        prices = {}
        for crypto in cryptos:
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd&include_24hr_change=true'
            data = requests.get(url).json()
            prices[crypto] = {
                'price': data[crypto]['usd'],
                'change': data[crypto]['usd_24h_change']
            }
        return prices

    prices = get_crypto_prices()

    for crypto, data in prices.items():
        st.metric(label=crypto.capitalize(), value=f"${data['price']:.2f}", delta=f"{data['change']:.2f}%")

    st.markdown("🔄 Data refreshes every 15 seconds")

# Auto-refresh
time.sleep(15)
st.experimental_rerun()
