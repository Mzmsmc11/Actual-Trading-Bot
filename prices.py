"""
Scheduled price checks for the channel: tracks a fixed watchlist, posts
alerts when something moves more than PRICE_ALERT_THRESHOLD_PCT, and
posts a periodic snapshot of everything being tracked.

Crypto: CoinGecko (free, no key).
Forex: Frankfurter.app / ECB reference rates (free, no key, updates once
per business day - fine for context, not real intraday movement). Swap
in a paid provider here later if you need live forex ticks.
"""

import json
import os
import requests
from config import (
    CRYPTO_WATCHLIST,
    FOREX_WATCHLIST,
    LAST_PRICES_FILE,
    PRICE_ALERT_THRESHOLD_PCT,
)

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
FRANKFURTER_URL = "https://api.frankfurter.app/latest"


def get_crypto_prices() -> dict:
    ids = ",".join(CRYPTO_WATCHLIST.keys())
    try:
        resp = requests.get(
            COINGECKO_URL, params={"ids": ids, "vs_currencies": "usd"}, timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[prices] crypto fetch failed: {e}")
        return {}

    out = {}
    for coingecko_id, symbol in CRYPTO_WATCHLIST.items():
        if coingecko_id in data:
            out[symbol] = data[coingecko_id]["usd"]
    return out


def get_forex_rates() -> dict:
    out = {}
    for base, quotes in FOREX_WATCHLIST.items():
        try:
            resp = requests.get(
                FRANKFURTER_URL,
                params={"from": base, "to": ",".join(quotes)},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            print(f"[prices] forex fetch failed for {base}: {e}")
            continue
        for quote, rate in data.get("rates", {}).items():
            out[f"{base}->{quote}"] = rate
    return out


def _load_last_prices() -> dict:
    if os.path.exists(LAST_PRICES_FILE):
        try:
            with open(LAST_PRICES_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_last_prices(prices: dict) -> None:
    with open(LAST_PRICES_FILE, "w") as f:
        json.dump(prices, f)


def build_price_snapshot(crypto: dict, forex: dict) -> str:
    lines = ["📊 <b>Market Snapshot</b>"]
    if crypto:
        lines.append("\n<b>Crypto</b>")
        for symbol, price in crypto.items():
            lines.append(f"{symbol}: ${price:,.2f}")
    if forex:
        lines.append("\n<b>Forex</b>")
        for pair, rate in forex.items():
            lines.append(f"{pair.replace('->', '/')}: {rate:.4f}")
    return "\n".join(lines)


def check_for_moves(crypto: dict, forex: dict) -> list:
    last = _load_last_prices()
    alerts = []
    current = {**{f"crypto:{k}": v for k, v in crypto.items()},
               **{f"forex:{k}": v for k, v in forex.items()}}

    for key, new_price in current.items():
        old_price = last.get(key)
        if old_price:
            pct_change = ((new_price - old_price) / old_price) * 100
            if abs(pct_change) >= PRICE_ALERT_THRESHOLD_PCT:
                kind, label = key.split(":", 1)
                direction = "🟢 UP" if pct_change > 0 else "🔴 DOWN"
                display_label = label.replace("->", "/")
                fmt = f"{new_price:,.4f}" if kind == "forex" else f"${new_price:,.2f}"
                alerts.append(
                    f"⚡ <b>{display_label}</b> {direction} {abs(pct_change):.2f}%\nNow: {fmt}"
                )

    _save_last_prices(current)
    return alerts
