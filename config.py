"""
Central configuration. Fill in real values via environment variables
(locally: a .env file copied from .env.example; on Railway: the Variables tab).
Do not hardcode secrets here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---- Telegram ----
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# Channel username (e.g. "@my_channel") or numeric chat id (e.g. -1001234567890)
# Leave blank until you've created the channel - the bot will still run and
# respond to DM commands, it just won't have anywhere to post news/prices yet.
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# ---- Timing (seconds) ----
NEWS_CHECK_INTERVAL = int(os.getenv("NEWS_CHECK_INTERVAL", "180"))
PRICE_CHECK_INTERVAL = int(os.getenv("PRICE_CHECK_INTERVAL", "300"))
PRICE_ALERT_THRESHOLD_PCT = float(os.getenv("PRICE_ALERT_THRESHOLD_PCT", "1.5"))

# ---- News sources (RSS) ----
# Feed URLs occasionally move - if one stops producing stories, swap it out.
RSS_FEEDS = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("CoinTelegraph", "https://cointelegraph.com/rss"),
    ("Decrypt", "https://decrypt.co/feed"),
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
    ("Investing.com", "https://www.investing.com/rss/news.rss"),
]

# ---- Crypto watchlist for the channel's scheduled alerts/snapshots ----
# (CoinGecko IDs -> display symbol). This is separate from /price, which
# works for any coin on request.
CRYPTO_WATCHLIST = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "ripple": "XRP",
    "binancecoin": "BNB",
}

# ---- Forex pairs for the channel's scheduled alerts/snapshots ----
FOREX_WATCHLIST = {
    "USD": ["EUR", "GBP", "JPY"],
    "GBP": ["USD", "EUR"],
}

# ---- Persistence (local files, created automatically) ----
SEEN_LINKS_FILE = "seen_links.json"
LAST_PRICES_FILE = "last_prices.json"
LAST_UPDATE_ID_FILE = "last_update_id.json"
