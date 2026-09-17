"""
Central configuration for the news + price bot.
Fill in the values in .env (copy .env.example -> .env) rather than editing this file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---- Telegram ----
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# Channel username (e.g. "@my_channel") or numeric chat id (e.g. -1001234567890)
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# ---- Timing (seconds) ----
NEWS_CHECK_INTERVAL = int(os.getenv("NEWS_CHECK_INTERVAL", "180"))      # how often to poll RSS feeds
PRICE_CHECK_INTERVAL = int(os.getenv("PRICE_CHECK_INTERVAL", "300"))    # how often to check prices
PRICE_ALERT_THRESHOLD_PCT = float(os.getenv("PRICE_ALERT_THRESHOLD_PCT", "1.5"))  # % move that triggers an alert

# ---- News sources (RSS) ----
# NOTE: RSS feed URLs change over time. Verify these still resolve, and add/remove
# freely. Each entry is (label, feed_url).
RSS_FEEDS = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("CoinTelegraph", "https://cointelegraph.com/rss"),
    ("Decrypt", "https://decrypt.co/feed"),
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
    ("Investing.com", "https://www.investing.com/rss/news.rss"),
]

# ---- Crypto watchlist (CoinGecko IDs) ----
CRYPTO_WATCHLIST = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "ripple": "XRP",
    "binancecoin": "BNB",
}

# ---- Forex pairs to watch ----
# Base currency -> list of quote currencies (Frankfurter.app format, ECB daily rates)
FOREX_WATCHLIST = {
    "USD": ["EUR", "GBP", "JPY"],
    "GBP": ["USD", "EUR"],
}

# ---- Persistence ----
SEEN_LINKS_FILE = "seen_links.json"
LAST_PRICES_FILE = "last_prices.json"
