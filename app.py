import streamlit as st
import feedparser
import requests
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from urllib.parse import parse_qs

# Menghilangkan sidebar default
st.set_page_config(page_title="Bloomberg Style Dashboard", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------
# 1) Daftar feed
# -----------------------------
RSS_FEEDS = {
    "NEWEST": [
        "https://www.cnbc.com/id/20910258/device/rss/rss.html",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "https://www.reutersagency.com/feed/?best-topics=business-finance",
        # Tambahkan feed lainnya...
        "https://coinvestasi.com/feed"
    ],
    "Coinvestasi": "https://coinvestasi.com/feed",
    "Reuters": "https://www.reutersagency.com/feed/?best-topics=markets",
}

# -----------------------------
# 2) Fungsi fetch data
# -----------------------------
def fetch_news(url, max_entries=5):
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
    if r.status_code != 200:
        return []
    parsed = feedparser.parse(r.text)
    data = []
    for entry in parsed.entries[:max_entries]:
        # parse time
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_time = time.mktime(entry.published_parsed)
        else:
            published_time = 0
        summary = entry.summary[:300] + "..." if hasattr(entry, 'summary') else ""
        data.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "published_time": published_time
        })
    return data

def get_crypto_prices():
    base = {
        "bitcoin": {"usd":0, "usd_24h_change":0},
        "ethereum": {"usd":0, "usd_24h_change":0},
        "solana": {"usd":0, "usd_24h_change":0}
    }
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=bitcoin,ethereum,solana"
        "&vs_currencies=usd"
        "&include_24hr_change=true"
    )
    try:
        resp = requests.get(url, timeout=5).json()
        for coin in base:
            if coin in resp:
                base[coin]["usd"] = resp[coin].get("usd",0)
                base[coin]["usd_24h_change"] = resp[coin].get("usd_24h_change",0)
    except:
        pass
    return base

# -----------------------------
# 3) Ambil feed_choice dari URL param
# -----------------------------
query_params = st.experimental_get_query_params()
feed_choice = query_params.get("feed", ["NEWEST"])[0]
# Pastikan valid
if feed_choice not in RSS_FEEDS:
    feed_choice = "NEWEST"

# -----------------------------
# 4) Ambil data feed
# -----------------------------
if isinstance(RSS_FEEDS[feed_choice], list):
    # "NEWEST"
    all_news = []
    for feed_url in RSS_FEEDS[feed_choice]:
        all_news.extend(fetch_news(feed_url, 3))  # fetch 3 per feed
    all_news.sort(key=lambda x: x["published_time"], reverse=True)
else:
    # single feed
    all_news = fetch_news(RSS_FEEDS[feed_choice], 10)
    all_news.sort(key=lambda x: x["published_time"], reverse=True)

news_show = all_news[:10]  # 10 item

# -----------------------------
# 5) Ambil data crypto
# -----------------------------
crypto_prices = get_crypto_prices()

# -----------------------------
# 6) Generate HTML bergaya
# -----------------------------
html_head = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Bloomberg Style Dashboard</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: Consolas, 'Courier New', monospace;
    background-color: #191919;
    color: #E6E6E6;
    height: 100vh;
    display: flex; flex-direction: column;
  }
  header {
    background-color:#333;
    padding: 12px 20px;
    display: flex;
    justify-content:space-between;
    align-items:center;
  }
  header .logo {
    color:#FFD100; 
    font-size:1.2rem;
    text-transform: uppercase;
  }
  header .menu a {
    color: #E6E6E6; 
    text-decoration: none; 
    margin-left:20px;
  }
  /* feed dropdown di top bar */
  .feed-select {
    background-color:#555; 
    color:#E6E6E6; 
    border:none;
    padding:4px;
    font-family: inherit;
  }
  .container {
    flex:1; display:flex; 
    height:calc(100vh - 50px);
  }
  aside {
    width:280px; background-color:#1E1E1E; 
    border-right:1px solid #333;
    padding:20px;
  }
  aside h2 {
    color:#FFD100; font-size:1rem; margin-bottom:10px;
  }
  .ticker { 
    display:flex; justify-content:space-between; 
    padding:4px 0;
  }
  .ticker .price-up { color:#00FF00; }
  .ticker .price-down { color:#FF3333; }

  main {
    flex:1; padding:20px; overflow-y:auto;
  }
  h2.section-title {
    font-size:1.3rem; margin-bottom:10px; color:#FFD100;
  }
  .headline {
    border-bottom:1px solid #333; padding-bottom:10px; margin-bottom:10px;
  }
  .headline .time {
    color:#AAAAAA; font-size:0.85rem; margin: 5px 0;
  }
  .headline a {
    color:#62B0E8; text-decoration:none;
  }
  .news-list .news-item {
    border-bottom:1px solid #333; margin-bottom:10px; padding-bottom:10px;
  }
  .news-item a {
    color:#62B0E8; text-decoration:none;
  }
  .news-item a:hover { text-decoration:underline; }
  .time-small {
    color:#AAAAAA; font-size:0.85rem;
  }

  /* scrollbar */
  ::-webkit-scrollbar{ width:8px; }
  ::-webkit-scrollbar-thumb{ background:#333; }
  ::-webkit-scrollbar-track{ background:#1E1E1E; }
</style>
</head>
<body>
"""

html_topbar = f"""
<header>
  <div class="logo">My Terminal</div>
  <div class="menu">
    <select class="feed-select" onchange="location.href='?feed='+this.value">
"""

# Buat <option> feed
options_html = ""
for k in RSS_FEEDS.keys():
    selected = "selected" if k == feed_choice else ""
    options_html += f'<option value="{k}" {selected}>{k}</option>'

html_topbar2 = f"""
    </select>
    <a href="#">Markets</a>
    <a href="#">Crypto</a>
    <a href="#">Macro</a>
  </div>
</header>
"""

html_container_start = """
<div class="container">
  <aside>
    <h2>Watchlist</h2>
"""

html_container_end = """
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

# watchlist
def format_watchlist(label, price, change):
    if change >= 0:
        return f"""
        <div class="ticker">
          <span>{label}</span>
          <span class="price-up">{price:.2f}</span>
        </div>
        """
    else:
        return f"""
        <div class="ticker">
          <span>{label}</span>
          <span class="price-down">{price:.2f}</span>
        </div>
        """

watchlist_html = (
    format_watchlist("BTC/USD", crypto_prices["bitcoin"]["usd"], crypto_prices["bitcoin"]["usd_24h_change"]) +
    format_watchlist("ETH/USD", crypto_prices["ethereum"]["usd"], crypto_prices["ethereum"]["usd_24h_change"]) +
    format_watchlist("SOL/USD", crypto_prices["solana"]["usd"], crypto_prices["solana"]["usd_24h_change"])
)

# HEADLINE + 9 BERITA
news_html = ""
if news_show:
    # HEADLINE
    headline = news_show[0]
    dt_head = datetime.fromtimestamp(headline["published_time"]).strftime("%a, %d %b %Y %H:%M:%S UTC")

    news_html += f"""
    <div class="headline">
      <div class="time">{dt_head}</div>
      <a href="{headline['link']}" target="_blank"><strong>{headline['title']}</strong></a>
      <p>{headline['summary']}</p>
    </div>
    <div class="news-list">
    """

    for item in news_show[1:10]:
        dt_item = datetime.fromtimestamp(item["published_time"]).strftime("%a, %d %b %Y %H:%M:%S UTC")
        news_html += f"""
        <div class="news-item">
          <div class="time-small">{dt_item}</div>
          <a href="{item['link']}" target="_blank"><strong>{item['title']}</strong></a>
          <p>{item['summary']}</p>
        </div>
        """
    news_html += "</div>"
else:
    news_html += "<p>No news available.</p>"

# Susun final HTML
final_html = (
    html_head
    + html_topbar
    + options_html
    + html_topbar2
    + html_container_start
    + watchlist_html
    + html_container_end
    + news_html
    + html_footer
)

# Tampilkan
st.components.v1.html(final_html, height=800, scrolling=True)

# Auto-refresh 15 detik
st_autorefresh(interval=15_000, limit=None, key="bbg_refresher")
