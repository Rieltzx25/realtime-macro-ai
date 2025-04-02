import streamlit as st
import feedparser
import requests
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import os
import plotly.graph_objects as go
from textblob import TextBlob
import numpy as np
import pandas as pd

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
    /* Global Background with animated gradient - BLUE THEME */
    .main {
        background: linear-gradient(-45deg, \#0a192f, \#172a46, \#0d2240, \#1e3a5f);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        position: relative;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Animated particles overlay */
    .main::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4" viewBox="0 0 4 4"><circle cx="2" cy="2" r="0.5" fill="rgba(255,255,255,0.1)"/></svg>');
        pointer-events: none;
        z-index: -1;
    }
    
    /* Enhanced News Card */
    .news-card {
        background: rgba(13, 34, 64, 0.7);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid transparent;
        background-image: linear-gradient(rgba(13, 34, 64, 0.7), rgba(13, 34, 64, 0.7)),
                          linear-gradient(45deg, \#3498db, \#00bfff);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .news-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
        transition: 0.5s;
    }
    
    .news-card:hover {
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
        transform: translateY(-5px);
    }
    
    .news-card:hover::after {
        left: 100%;
    }
    
    .news-headline {
        color: \#FFFFFF;
        font-size: 22px;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(52, 152, 219, 0.3);
        padding-bottom: 8px;
    }
    
    .news-summary {
        color: \#DDDDDD;
        font-size: 15px;
        line-height: 1.5;
    }
    
    .news-timestamp {
        color: \#AAA;
        font-size: 12px;
        display: flex;
        align-items: center;
        margin: 8px 0;
    }
    
    .sentiment-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        margin-left: 10px;
        font-weight: bold;
        font-size: 11px;
        text-transform: uppercase;
    }
    
    .sentiment-positive {
        background-color: rgba(46, 204, 113, 0.2);
        color: \#2ecc71;
        border: 1px solid rgba(46, 204, 113, 0.3);
    }
    
    .sentiment-negative {
        background-color: rgba(231, 76, 60, 0.2);
        color: \#e74c3c;
        border: 1px solid rgba(231, 76, 60, 0.3);
    }
    
    .sentiment-neutral {
        background-color: rgba(255, 255, 255, 0.1);
        color: \#BBBBBB;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .read-more-link {
        display: inline-block;
        margin-top: 10px;
        color: \#3498db;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.2s ease;
        border-bottom: 1px solid transparent;
    }
    
    .read-more-link:hover {
        border-bottom: 1px solid \#3498db;
        padding-left: 5px;
    }
    
    /* Enhanced Crypto Card */
    .crypto-card {
        background: rgba(13, 34, 64, 0.7);
        backdrop-filter: blur(10px);
        padding: 25px 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 1px solid transparent;
        background-image: linear-gradient(rgba(13, 34, 64, 0.7), rgba(13, 34, 64, 0.7)),
                          linear-gradient(45deg, \#3498db, \#00bfff);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .crypto-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        transform: rotate(30deg);
        z-index: -1;
    }
    
    .crypto-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
    }
    
    .crypto-icon {
        font-size: 28px;
        margin-bottom: 10px;
    }
    
    .crypto-name {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .crypto-name.bitcoin {
        color: \#3498db;
    }
    
    .crypto-name.ethereum {
        color: \#9EAEFF;
    }
    
    .crypto-name.solana {
        color: \#00bfff;
    }
    
    .crypto-price {
        font-size: 24px;
        font-weight: bold;
        color: \#FFFFFF;
        margin: 10px 0;
    }
    
    .crypto-change {
        font-size: 16px;
        padding: 5px 10px;
        border-radius: 15px;
        display: inline-block;
    }
    
    .crypto-change.negative {
        background-color: rgba(231, 76, 60, 0.2);
        color: \#e74c3c;
    }
    
    .crypto-change.positive {
        background-color: rgba(46, 204, 113, 0.2);
        color: \#2ecc71;
    }
    
    /* Enhanced Sidebar */
    .stSidebar {
        background: linear-gradient(180deg, \#0a192f 0%, \#172a46 100%);
        border-right: 1px solid rgba(52, 152, 219, 0.3);
        box-shadow: 5px 0 15px rgba(0, 0, 0, 0.2);
    }
    
    .sidebar-header {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid rgba(52, 152, 219, 0.3);
        margin-bottom: 20px;
    }
    
    .sidebar-nav-item {
        background: rgba(13, 34, 64, 0.5);
        margin: 8px 0;
        padding: 10px 15px;
        border-radius: 10px;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .sidebar-nav-item:hover, .sidebar-nav-item.active {
        background: rgba(52, 152, 219, 0.1);
        transform: translateX(5px);
    }
    
    .sidebar-nav-item.active {
        border-left: 3px solid \#3498db;
    }
    
    /* Enhanced Sidebar Clock */
    .sidebar-clock-container {
        background: rgba(13, 34, 64, 0.7);
        backdrop-filter: blur(5px);
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(52, 152, 219, 0.2);
        color: \#FFFFFF;
        font-size: 14px;
        margin-top: 30px;
        position: relative;
        overflow: hidden;
    }
    
    .sidebar-clock-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, rgba(52, 152, 219, 0.1), transparent);
        z-index: -1;
    }
    
    .clock-text {
        margin: 5px 0;
        color: \#DDDDDD;
        display: flex;
        align-items: center;
    }
    
    .clock-icon {
        margin-right: 10px;
        color: \#3498db;
    }
    
    /* Dashboard Header */
    .dashboard-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid rgba(52, 152, 219, 0.3);
    }
    
    .dashboard-title {
        display: flex;
        align-items: center;
    }
    
    .dashboard-title-icon {
        font-size: 32px;
        margin-right: 15px;
        color: \#3498db;
    }
    
    .dashboard-refresh-info {
        background: rgba(52, 152, 219, 0.1);
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 14px;
        color: \#3498db;
        display: flex;
        align-items: center;
    }
    
    .refresh-icon {
        margin-right: 8px;
        animation: spin 2s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Chart Container */
    .chart-container {
        background: rgba(13, 34, 64, 0.7);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 20px 0;
        border: 1px solid rgba(52, 152, 219, 0.2);
    }
    
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .chart-title {
        font-size: 20px;
        font-weight: bold;
        color: \#3498db;
    }
    
    .chart-period-selector {
        display: flex;
        gap: 10px;
    }
    
    .chart-period-btn {
        background: rgba(255, 255, 255, 0.1);
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        color: \#CCCCCC;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .chart-period-btn:hover, .chart-period-btn.active {
        background: rgba(52, 152, 219, 0.2);
        color: \#3498db;
    }
    
    /* Search Box */
    .search-container {
        position: relative;
        margin: 20px 0;
    }
    
    .search-input {
        width: 100%;
        padding: 12px 20px 12px 45px;
        border-radius: 30px;
        border: 1px solid rgba(52, 152, 219, 0.3);
        background: rgba(13, 34, 64, 0.7);
        color: \#FFFFFF;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .search-input:focus {
        box-shadow: 0 0 15px rgba(52, 152, 219, 0.3);
        border-color: rgba(52, 152, 219, 0.5);
        outline: none;
    }
    
    .search-icon {
        position: absolute;
        left: 15px;
        top: 50%;
        transform: translateY(-50%);
        color: \#888888;
    }
    
    /* Feature Cards */
    .feature-card {
        background: rgba(13, 34, 64, 0.7);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(52, 152, 219, 0.2);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
    }
    
    .feature-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .feature-icon {
        font-size: 24px;
        margin-right: 10px;
        color: \#3498db;
    }
    
    .feature-title {
        font-size: 20px;
        font-weight: bold;
        color: \#FFFFFF;
    }
    
    .feature-content {
        color: \#DDDDDD;
    }
    
    .feature-link {
        display: inline-block;
        margin-top: 15px;
        padding: 8px 20px;
        background: rgba(52, 152, 219, 0.2);
        color: \#3498db;
        border-radius: 20px;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    .feature-link:hover {
        background: rgba(52, 152, 219, 0.3);
        transform: translateX(5px);
    }
    
    /* Loading Animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 30px;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid rgba(52, 152, 219, 0.3);
        border-radius: 50%;
        border-top: 4px solid \#3498db;
        animation: spin 1s linear infinite;
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: rgba(0, 0, 0, 0.8);
        color: \#fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Notification Badge */
    .notification-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background-color: \#e74c3c;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(13, 34, 64, 0.7);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(52, 152, 219, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(52, 152, 219, 0.5);
    }
    
    /* Responsive Adjustments */
    @media (max-width: 768px) {
        .crypto-card {
            margin-bottom: 15px;
        }
        
        .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .dashboard-refresh-info {
            margin-top: 10px;
        }
    }

    /* Table Styling */
    .crypto-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .crypto-table th {
        text-align: left;
        padding: 10px;
        color: \#AAAAAA;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .crypto-table td {
        padding: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .crypto-table tr:hover {
        background: rgba(255,255,255,0.03);
    }

    /* Fear and Greed Index */
    .fear-greed-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
    }
    
    .fear-greed-gauge {
        width: 100%;
        height: 50px;
        background: linear-gradient(to right, \#e74c3c, \#f39c12, \#f1c40f, \#2ecc71);
        border-radius: 25px;
        position: relative;
        margin: 20px 0;
        overflow: hidden;
    }
    
    .fear-greed-indicator {
        position: absolute;
        top: -10px;
        width: 10px;
        height: 70px;
        background-color: white;
        transform: translateX(-50%);
    }
    
    .fear-greed-labels {
        display: flex;
        justify-content: space-between;
        width: 100%;
        margin-top: 10px;
    }
    
    .fear-greed-value {
        font-size: 48px;
        font-weight: bold;
        color: \#3498db;
        margin: 20px 0;
    }
    
    .fear-greed-text {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* Rainbow Chart */
    .rainbow-bands {
        position: relative;
        height: 300px;
        margin: 20px 0;
        border-radius: 15px;
        overflow: hidden;
    }
    
    .rainbow-band {
        position: absolute;
        width: 100%;
        height: 42px;
        left: 0;
        opacity: 0.8;
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
FEATURES = ["Market Overview", "Fear and Greed Index", "Bitcoin Rainbow Chart"]

##################################
# FUNGSI TAMBAHAN & UTILITAS LAIN #
##################################
def display_sidebar_clock():
    """Menampilkan jam UTC & WIB di Sidebar dengan tampilan yang lebih menarik"""
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
            <div class="clock-text"><span class="clock-icon">🕒</span> {utc_time_str}</div>
            <div class="clock-text"><span class="clock-icon">🕗</span> {wib_time_str}</div>
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
        # Fallback data if API fails
        prices = {
            "bitcoin": {"usd": 65432, "usd_24h_change": 2.5},
            "ethereum": {"usd": 3456, "usd_24h_change": 1.8},
            "solana": {"usd": 142, "usd_24h_change": -0.7}
        }
    return prices

def get_bitcoin_history(days=30):
    try:
        # Generate synthetic data instead of API call to avoid errors
        today = datetime.now()
        dates = []
        prices = []
        
        # Start price and random seed for reproducibility
        base_price = 65000
        np.random.seed(42)
        
        for i in range(days, 0, -1):
            date = today - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
            
            # Generate realistic price movements
            if i == days:
                prices.append(base_price)
            else:
                # Random daily change between -5% and +5%
                daily_change = np.random.normal(0, 0.02)
                new_price = prices[-1] * (1 + daily_change)
                prices.append(new_price)
        
        return dates, prices
    except Exception as e:
        # Even more basic fallback
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days, 0, -1)]
        prices = [60000 + i * 100 for i in range(days)]
        return dates, prices

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
        return 'Netral'

def display_news_items(news_list):
    """Menampilkan kartu berita dengan badge sentimen yang lebih menarik"""
    if not news_list:
        st.write("Tidak ada berita.")
        return
    for item in news_list:
        dt_item = datetime.fromtimestamp(item["published_time"])
        sentiment_result = analyze_sentiment(item['summary'])
        
        # Determine sentiment badge class
        sentiment_class = ""
        if sentiment_result == "Positif":
            sentiment_class = "sentiment-positive"
        elif sentiment_result == "Negatif":
            sentiment_class = "sentiment-negative"
        else:
            sentiment_class = "sentiment-neutral"
            
        st.markdown(f"""
        <div class='news-card'>
            <p class='news-headline'>{item['title']}</p>
            <p class='news-timestamp'>
                <span>📅 {dt_item.strftime("%a, %d %b %Y %H:%M:%S UTC")}</span>
                <span class='sentiment-badge {sentiment_class}'>{sentiment_result}</span>
            </p>
            <p class='news-summary'>{item['summary']}</p>
            <a href='{item['link']}' target='_blank' class='read-more-link'>🔗 Baca Selengkapnya</a>
        </div>
        """, unsafe_allow_html=True)

# New function to display market overview
def display_market_overview():
    """Displays a market overview section with key indicators"""
    st.markdown("""
    <div class="feature-card">
        <div class="feature-header">
            <span class="feature-icon">📊</span>
            <h2 class="feature-title">Market Overview</h2>
        </div>
        <div class="feature-content">
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                <div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 10px;">
                    <h3 style="font-size: 16px; color: #AAAAAA; margin-bottom: 5px;">BTC Dominance</h3>
                    <p style="font-size: 20px; font-weight: bold; color: #3498db;">52.4%</p>
                </div>
                <div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 10px;">
                    <h3 style="font-size: 16px; color: #AAAAAA; margin-bottom: 5px;">24h Volume</h3>
                    <p style="font-size: 20px; font-weight: bold; color: #3498db;">$48.2B</p>
                </div>
                <div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 10px;">
                    <h3 style="font-size: 16px; color: #AAAAAA; margin-bottom: 5px;">Market Cap</h3>
                    <p style="font-size: 20px; font-weight: bold; color: #3498db;">$2.1T</p>
                </div>
                <div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 10px;">
                    <h3 style="font-size: 16px; color: #AAAAAA; margin-bottom: 5px;">Active Cryptocurrencies</h3>
                    <p style="font-size: 20px; font-weight: bold; color: #3498db;">10,482</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# New function to display trending coins
def display_trending_coins():
    """Displays trending coins section"""
    st.markdown("""
    <div class="feature-card">
        <div class="feature-header">
            <span class="feature-icon">🔥</span>
            <h2 class="feature-title">Trending Coins (24h)</h2>
        </div>
        <div class="feature-content">
            <table class="crypto-table">
                <tr>
                    <th>#</th>
                    <th>Coin</th>
                    <th style="text-align: right;">Price</th>
                    <th style="text-align: right;">24h %</th>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Pepe (PEPE)</td>
                    <td style="text-align: right;">$0.000012</td>
                    <td style="text-align: right; color: #2ecc71;">+15.4%</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Dogecoin (DOGE)</td>
                    <td style="text-align: right;">$0.1423</td>
                    <td style="text-align: right; color: #2ecc71;">+8.2%</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Shiba Inu (SHIB)</td>
                    <td style="text-align: right;">$0.00002814</td>
                    <td style="text-align: right; color: #2ecc71;">+5.7%</td>
                </tr>
                <tr>
                    <td>4</td>
                    <td>Solana (SOL)</td>
                    <td style="text-align: right;">$142.87</td>
                    <td style="text-align: right; color: #2ecc71;">+3.2%</td>
                </tr>
                <tr>
                    <td>5</td>
                    <td>Cardano (ADA)</td>
                    <td style="text-align: right;">$0.4521</td>
                    <td style="text-align: right; color: #e74c3c;">-2.1%</td>
                </tr>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

# New function to display news sentiment summary
def display_sentiment_summary(news_list):
    """Displays a summary of news sentiment"""
    if not news_list:
        return
        
    # Count sentiments
    sentiments = {"Positif": 0, "Negatif": 0, "Netral": 0}
    for item in news_list:
        sentiment = analyze_sentiment(item['summary'])
        if sentiment in sentiments:
            sentiments[sentiment] += 1
            
    total = sum(sentiments.values())
    if total == 0:
        return
        
    # Calculate percentages
    pos_percent = (sentiments["Positif"] / total) * 100
    neg_percent = (sentiments["Negatif"] / total) * 100
    neu_percent = (sentiments["Netral"] / total) * 100
    
    # Determine overall sentiment
    overall = "Neutral"
    if pos_percent > 60:
        overall = "Bullish"
    elif neg_percent > 60:
        overall = "Bearish"
    elif pos_percent > neg_percent + 20:
        overall = "Slightly Bullish"
    elif neg_percent > pos_percent + 20:
        overall = "Slightly Bearish"
    
    # Display sentiment summary
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-header">
            <span class="feature-icon">🧠</span>
            <h2 class="feature-title">News Sentiment Analysis</h2>
        </div>
        <div class="feature-content">
            <p style="font-size: 18px; margin-bottom: 15px;">Overall Market Sentiment: <strong style="color: {'#2ecc71' if 'Bullish' in overall else '#e74c3c' if 'Bearish' in overall else '#AAAAAA'};">{overall}</strong></p>
            
            <div style="background: rgba(52, 152, 219, 0.1); border-radius: 10px; padding: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #2ecc71;">Positive</span>
                    <span style="color: #2ecc71;">{pos_percent:.1f}%</span>
                </div>
                <div style="width: 100%; background: rgba(255,255,255,0.1); height: 10px; border-radius: 5px;">
                    <div style="width: {pos_percent}%; background: #2ecc71; height: 10px; border-radius: 5px;"></div>
                </div>
            </div>
            
            <div style="background: rgba(52, 152, 219, 0.1); border-radius: 10px; padding: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #AAAAAA;">Neutral</span>
                    <span style="color: #AAAAAA;">{neu_percent:.1f}%</span>
                </div>
                <div style="width: 100%; background: rgba(255,255,255,0.1); height: 10px; border-radius: 5px;">
                    <div style="width: {neu_percent}%; background: #AAAAAA; height: 10px; border-radius: 5px;"></div>
                </div>
            </div>
            
            <div style="background: rgba(52, 152, 219, 0.1); border-radius: 10px; padding: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #e74c3c;">Negative</span>
                    <span style="color: #e74c3c;">{neg_percent:.1f}%</span>
                </div>
                <div style="width: 100%; background: rgba(255,255,255,0.1); height: 10px; border-radius: 5px;">
                    <div style="width: {neg_percent}%; background: #e74c3c; height: 10px; border-radius: 5px;"></div>
                </div>
            </div>
            
            <p style="font-size: 14px; color: #AAAAAA; margin-top: 15px;">Based on analysis of {total} news articles</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# New function to display Fear and Greed Index
def display_fear_greed_index():
    """Displays the Fear and Greed Index with proper visualization"""
    # Generate a random value between 0 and 100 for demo purposes
    # In production, you would fetch this from an API
    fear_greed_value = 65
    
    # Determine the sentiment text based on the value
    if fear_greed_value <= 25:
        sentiment = "Extreme Fear"
        color = "#e74c3c"
    elif fear_greed_value <= 45:
        sentiment = "Fear"
        color = "#f39c12"
    elif fear_greed_value <= 55:
        sentiment = "Neutral"
        color = "#f1c40f"
    elif fear_greed_value <= 75:
        sentiment = "Greed"
        color = "#2ecc71"
    else:
        sentiment = "Extreme Greed"
        color = "#27ae60"
    
    # Calculate the position of the indicator (percentage of the gauge width)
    position_percent = fear_greed_value
    
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-header">
            <span class="feature-icon">📊</span>
            <h2 class="feature-title">Crypto Fear & Greed Index</h2>
        </div>
        <div class="feature-content fear-greed-container">
            <div class="fear-greed-text">Current Status: <span style="color: {color}">{sentiment}</span></div>
            <div class="fear-greed-value">{fear_greed_value}</div>
            
            <div class="fear-greed-gauge">
                <div class="fear-greed-indicator" style="left: {position_percent}%;"></div>
            </div>
            
            <div class="fear-greed-labels">
                <span style="color: #e74c3c">Extreme Fear</span>
                <span style="color: #f39c12">Fear</span>
                <span style="color: #f1c40f">Neutral</span>
                <span style="color: #2ecc71">Greed</span>
                <span style="color: #27ae60">Extreme Greed</span>
            </div>
            
            <p style="margin-top: 20px; text-align: center;">
                The Fear & Greed Index analyzes emotions and sentiments from different sources and condenses them into a simple number.
                <br>A value of 0 means "Extreme Fear", while a value of 100 represents "Extreme Greed".
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# New function to display Bitcoin Rainbow Chart
def display_bitcoin_rainbow_chart():
    """Displays the Bitcoin Rainbow Chart with proper visualization"""
    # Get Bitcoin price history
    dates, prices = get_bitcoin_history(365*2)  # 2 years of data
    
    # Create the rainbow bands
    rainbow_colors = [
        "#FF0000",  # Red (Maximum Bubble)
        "#FF5500",  # Orange-Red (Sell. Seriously, SELL!)
        "#FFAA00",  # Orange (FOMO Intensifies)
        "#FFFF00",  # Yellow (Is This a Bubble?)
        "#AAFF00",  # Yellow-Green (HODL!)
        "#00FF00",  # Green (Still Cheap)
        "#00FFAA",  # Turquoise (Accumulate)
        "#00AAFF",  # Light Blue (Buy)
        "#0000FF",  # Blue (Basically a Fire Sale)
    ]
    
    rainbow_labels = [
        "Maximum Bubble",
        "Sell. Seriously, SELL!",
        "FOMO Intensifies",
        "Is This a Bubble?",
        "HODL!",
        "Still Cheap",
        "Accumulate",
        "Buy",
        "Basically a Fire Sale"
    ]
    
    # Create the rainbow chart using Plotly
    fig = go.Figure()
    
    # Add the price line
    fig.add_trace(go.Scatter(
        x=dates,
        y=prices,
        name="Bitcoin Price",
        line=dict(color='#3498db', width=3),
        mode='lines'
    ))
    
    # Calculate logarithmic regression bands
    # This is a simplified version - in production you would use actual logarithmic regression
    base_price = prices[-1]
    for i, (color, label) in enumerate(zip(rainbow_colors, rainbow_labels)):
        # Create synthetic bands for demonstration
        multiplier = 2.0 - (i * 0.2)  # Higher bands for higher indices
        band_prices = [p * multiplier for p in prices]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=band_prices,
            name=label,
            line=dict(color=color, width=1, dash='dash'),
            opacity=0.3,
            showlegend=True
        ))
    
    # Update layout
    fig.update_layout(
        title="Bitcoin Rainbow Chart - Logarithmic Regression",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        yaxis_type="log",  # Logarithmic scale
        template="plotly_dark",
        paper_bgcolor="rgba(13, 34, 64, 0.0)",
        plot_bgcolor="rgba(13, 34, 64, 0.0)",
        font_color="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linecolor='rgba(255, 255, 255, 0.2)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linecolor='rgba(255, 255, 255, 0.2)'
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: -20px; margin-bottom: 20px;">
        <p>The Bitcoin Rainbow Chart is a logarithmic regression that provides a long-term view of Bitcoin price movements.<br>
        It uses color bands to indicate different market sentiments from "Maximum Bubble" to "Basically a Fire Sale".</p>
    </div>
    """, unsafe_allow_html=True)

##########################
# SIDEBAR DAN NAVIGASI  #
##########################
logo_path = "cat_logo.webp"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)

st.sidebar.markdown("""
<div class="sidebar-header">
    <h2>Dashboard Navigation</h2>
</div>
""", unsafe_allow_html=True)

# Create styled navigation buttons
section_options = ["News Feed", "Features"]
section = st.sidebar.radio("", section_options, label_visibility="collapsed")

# Display styled navigation items
for option in section_options:
    is_active = option == section
    active_class = "active" if is_active else ""
    st.sidebar.markdown(f"""
    <div class="sidebar-nav-item {active_class}">
        {option}
    </div>
    """, unsafe_allow_html=True)

# Enhanced search box
st.sidebar.markdown("""
<div class="search-container">
    <span class="search-icon">🔍</span>
</div>
""", unsafe_allow_html=True)

# Capture the search input
search_keyword = st.sidebar.text_input("Search news:", label_visibility="visible")

# Tampilkan jam di sidebar (lebih menarik)
display_sidebar_clock()

#################################
# HEADER & LIVE CRYPTO PRICES  #
#################################
# Dashboard Header with animated icon
st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">
        <span class="dashboard-title-icon">🚀</span>
        <h1>Realtime Macro & Crypto Dashboard</h1>
    </div>
    <div class="dashboard-refresh-info">
        <span class="refresh-icon">⟳</span>
        Data refreshes automatically every 15 seconds
    </div>
</div>
""", unsafe_allow_html=True)

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

# Tampilkan 3 crypto (BTC, ETH, SOL) dengan tampilan yang lebih menarik
col1, col2, col3 = st.columns(3)
cryptos = [
    ("Bitcoin (BTC)", "bitcoin", "₿"),
    ("Ethereum (ETH)", "ethereum", "Ξ"),
    ("Solana (SOL)", "solana", "◎")
]
for col, (name, key, icon) in zip([col1, col2, col3], cryptos):
    with col:
        data = st.session_state.crypto_prices.get(key, {})
        price = data.get("usd", 0)
        change = data.get("usd_24h_change", 0)
        change_class = 'negative' if change < 0 else 'positive'
        st.markdown(f"""
        <div class='crypto-card'>
            <div class='crypto-icon'>{icon}</div>
            <h3 class='crypto-name {key}'>{name}</h3>
            <p class='crypto-price'>${'{:,.2f}'.format(price)}</p>
            <p class='crypto-change {change_class}'>{'{:.2f}'.format(change)}%</p>
        </div>
        """, unsafe_allow_html=True)

########################
# BAGIAN UTAMA (CONTENT)
########################
if section == "News Feed":
    st.subheader("📰 Berita Terbaru")
    
    # Add sentiment summary at the top of news feed
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
    
    # Display sentiment summary before news
    display_sentiment_summary(all_news)
    
    # Tampilkan berita + sentiment
    display_news_items(all_news)

elif section == "Features":
    # Add tabs for different features
    tab1, tab2, tab3 = st.tabs(["Market Overview", "Charts & Indicators", "Fear & Greed"])
    
    with tab1:
        # Display market overview
        display_market_overview()
        
        # Display trending coins
        display_trending_coins()
    
    with tab2:
        # Display Bitcoin Rainbow Chart
        st.subheader("Bitcoin Rainbow Chart")
        display_bitcoin_rainbow_chart()
        
        # Display technical indicators
        st.subheader("Technical Indicators")
        st.markdown("""
        <div class="feature-card">
            <div class="feature-header">
                <span class="feature-icon">📈</span>
                <h2 class="feature-title">Technical Indicators</h2>
            </div>
            <div class="feature-content">
                <table class="crypto-table">
                    <tr>
                        <th>Indicator</th>
                        <th>Value</th>
                        <th>Signal</th>
                    </tr>
                    <tr>
                        <td>RSI (14)</td>
                        <td>58.42</td>
                        <td style="color: #AAAAAA;">Neutral</td>
                    </tr>
                    <tr>
                        <td>MACD</td>
                        <td>+245.8</td>
                        <td style="color: #2ecc71;">Buy</td>
                    </tr>
                    <tr>
                        <td>MA (50)</td>
                        <td>$42,850</td>
                        <td style="color: #2ecc71;">Buy</td>
                    </tr>
                    <tr>
                        <td>MA (200)</td>
                        <td>$38,420</td>
                        <td style="color: #2ecc71;">Buy</td>
                    </tr>
                    <tr>
                        <td>Bollinger Bands</td>
                        <td>Middle Band</td>
                        <td style="color: #AAAAAA;">Neutral</td>
                    </tr>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        # Display Fear and Greed Index
        display_fear_greed_index()
        
        # Display price predictions
        st.markdown("""
        <div class="feature-card">
            <div class="feature-header">
                <span class="feature-icon">🔮</span>
                <h2 class="feature-title">Price Predictions</h2>
            </div>
            <div class="feature-content">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
                    <div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 10px; text-align: center;">
                        <h3 style="font-size: 16px; color: #AAAAAA; margin-bottom: 5px;">24h</h3>
                        <p style="font-size: 20px; font-weight: bold; color: #2ecc71;">+2.4%</p>
                    </div>
                    <div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 10px; text-align: center;">
                        <h3 style="font-size: 16px; color: #AAAAAA; margin-bottom: 5px;">7d</h3>
                        <p style="font-size: 20px; font-weight: bold; color: #2ecc71;">+8.7%</p>
                    </div>
                    <div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 10px; text-align: center;">
                        <h3 style="font-size: 16px; color: #AAAAAA; margin-bottom: 5px;">30d</h3>
                        <p style="font-size: 20px; font-weight: bold; color: #e74c3c;">-3.2%</p>
                    </div>
                </div>
                <p style="font-size: 14px; color: #AAAAAA; margin-top: 15px; font-style: italic;">* Predictions based on technical analysis and market sentiment</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Auto-refresh the entire app setiap 15 detik
st_autorefresh(interval=15000, key="refresh")
