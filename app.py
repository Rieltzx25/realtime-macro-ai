import streamlit as st
import feedparser
import requests
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Bloomberg-Style Macro & Crypto Dashboard", layout="wide")

# --------------------------------------
# 1) Fungsi fetch data (berita + crypto)
# --------------------------------------

def fetch_news(url, max_entries=5):
    # Gunakan user-agent
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if resp.status_code != 200:
        return []
    feed = feedparser.parse(resp.text)

    news_data = []
    for entry in feed.entries[:max_entries]:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_time = time.mktime(entry.published_parsed)
        else:
            published_time = 0
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') else ""
        news_data.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "published_time": published_time
        })
    return news_data

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

# --------------------------------------
# 2) Daftar RSS feed
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
        "https://coinvestasi.com/feed"
    ],
    "Coinvestasi": "https://coinvestasi.com/feed"
    # Anda bisa tambahkan feed lain di sini
}

# --------------------------------------
# 3) Pilih feed & fetch data
# --------------------------------------
feed_choice = st.sidebar.selectbox("Pilih sumber berita", list(RSS_FEEDS.keys()))
if feed_choice == "NEWEST":
    all_news = []
    for feed_url in RSS_FEEDS["NEWEST"]:
        all_news.extend(fetch_news(feed_url, max_entries=2))
    # urutkan menurun
    all_news.sort(key=lambda x: x["published_time"], reverse=True)
else:
    all_news = fetch_news(RSS_FEEDS[feed_choice], max_entries=10)
    all_news.sort(key=lambda x: x["published_time"], reverse=True)

# Ambil 10 berita teratas
news_to_show = all_news[:10]

# Ambil data harga crypto
crypto_prices = get_crypto_prices()

# --------------------------------------
# 4) Buat HTML bergaya Bloomberg
# --------------------------------------
html_head = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Bloomberg-Style Dashboard</title>
  <style>
    /* Reset & base */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: Consolas, 'Courier New', monospace;
      background-color: #191919;
      color: #E6E6E6;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background-color: #333;
      padding: 12px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    header h1 {
      color: #FFD100; /* Kuning Bloomberg */
      font-size: 1.2rem;
    }
    header nav a {
      text-decoration: none;
      color: #E6E6E6;
      margin-left: 20px;
    }
    .container {
      display: flex;
      flex: 1;
      height: calc(100vh - 50px);
    }
    aside {
      width: 280px;
      background-color: #1E1E1E;
      border-right: 1px solid #333;
      padding: 20px;
      overflow-y: auto;
    }
    aside h2 {
      color: #FFD100;
      font-size: 1rem;
      margin-bottom: 10px;
    }
    .ticker {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
    }
    .ticker span.price-up { color: #00FF00; }
    .ticker span.price-down { color: #FF3333; }
    main {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
    }
    main h2.section-title {
      font-size: 1.3rem;
      margin-bottom: 10px;
      color: #FFD100;
    }
    .news-item {
      border-bottom: 1px solid #333;
      padding: 10px 0;
    }
    .news-item a {
      color: #62B0E8;
      text-decoration: none;
    }
    .news-item a:hover {
      text-decoration: underline;
    }
    .news-time {
      color: #AAAAAA;
      font-size: 0.85rem;
      margin-bottom: 4px;
    }
    /* scroll */
    ::-webkit-scrollbar {
      width: 8px;
    }
    ::-webkit-scrollbar-thumb {
      background: #333;
    }
    ::-webkit-scrollbar-track {
      background: #1E1E1E;
    }
  </style>
</head>
<body>
"""

html_body_start = """
<header>
  <h1>My Terminal</h1>
  <nav>
    <a href="#">Markets</a>
    <a href="#">Crypto</a>
    <a href="#">Macro News</a>
  </nav>
</header>

<div class="container">
  <aside>
    <h2>Watchlist</h2>
"""

html_body_end = """
  </aside>
  <main>
    <h2 class="section-title">Headline & Latest News</h2>
"""

html_footer = """
  </main>
</div>
</body>
</html>
"""

# --------------------------------------
# 5) Generate Watchlist (sidebar)
# --------------------------------------
# Contoh menampilkan 3 crypto
btc_price = f"{crypto_prices['bitcoin']['usd']:.2f}"
eth_price = f"{crypto_prices['ethereum']['usd']:.2f}"
sol_price = f"{crypto_prices['solana']['usd']:.2f}"

btc_change = crypto_prices['bitcoin']['usd_24h_change']
eth_change = crypto_prices['ethereum']['usd_24h_change']
sol_change = crypto_prices['solana']['usd_24h_change']

def format_ticker_row(label, price, change):
    if change >= 0:
        return f"""
        <div class="ticker">
          <span>{label}</span>
          <span class="price-up">{price}</span>
        </div>
        """
    else:
        return f"""
        <div class="ticker">
          <span>{label}</span>
          <span class="price-down">{price}</span>
        </div>
        """

watchlist_html = (
    format_ticker_row("BTC/USD", btc_price, btc_change) +
    format_ticker_row("ETH/USD", eth_price, eth_change) +
    format_ticker_row("SOL/USD", sol_price, sol_change)
)

# --------------------------------------
# 6) Generate News Section
# --------------------------------------
news_html = ""

if len(news_to_show) > 0:
    # HEADLINE
    headline = news_to_show[0]
    dt_head = datetime.fromtimestamp(headline["published_time"]).strftime("%a, %d %b %Y %H:%M:%S UTC")

    news_html += f"""
    <div class="news-item">
      <div class="news-time">{dt_head}</div>
      <a href="{headline['link']}" target="_blank"><strong>{headline['title']}</strong></a>
      <p>{headline['summary']}</p>
    </div>
    """

    # 9 Lainnya
    for item in news_to_show[1:10]:
        dt_item = datetime.fromtimestamp(item["published_time"]).strftime("%a, %d %b %Y %H:%M:%S UTC")
        news_html += f"""
        <div class="news-item">
          <div class="news-time">{dt_item}</div>
          <a href="{item['link']}" target="_blank"><strong>{item['title']}</strong></a>
          <p>{item['summary']}</p>
        </div>
        """
else:
    news_html += "<p>No news available</p>"

# --------------------------------------
# 7) Susun HTML penuh
# --------------------------------------
final_html = (
    html_head
    + html_body_start
    + watchlist_html
    + html_body_end
    + news_html
    + html_footer
)

# --------------------------------------
# 8) Tampilkan di Streamlit
# --------------------------------------
st.components.v1.html(final_html, height=800, scrolling=True)

# --------------------------------------
# 9) Auto-refresh tiap 15 detik
# --------------------------------------
st_autorefresh(interval=15_000, limit=None, key="news_refresher")
