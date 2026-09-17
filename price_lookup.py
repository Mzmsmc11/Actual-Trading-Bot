"""
On-demand price lookups for the /price command. Unlike prices.py (a fixed
watchlist for channel alerts), this resolves whatever the user typed.
"""

import re
import requests

COINGECKO_SEARCH_URL = "https://api.coingecko.com/api/v3/search"
COINGECKO_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"
FRANKFURTER_URL = "https://api.frankfurter.app/latest"

FOREX_CODES = {
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "NZD",
    "SEK", "NOK", "MXN", "SGD", "HKD", "INR", "ZAR", "TRY", "BRL",
}


def _looks_like_forex(query: str):
    cleaned = re.sub(r"[/\-\s]", "", query.upper())
    if len(cleaned) == 6 and cleaned[:3] in FOREX_CODES and cleaned[3:] in FOREX_CODES:
        return cleaned[:3], cleaned[3:]
    return None


def lookup_forex(base: str, quote: str):
    try:
        resp = requests.get(FRANKFURTER_URL, params={"from": base, "to": quote}, timeout=15)
        resp.raise_for_status()
        return resp.json().get("rates", {}).get(quote)
    except requests.RequestException as e:
        print(f"[price_lookup] forex lookup failed: {e}")
        return None


def lookup_crypto(query: str):
    """Returns (name, symbol, usd_price) or None."""
    try:
        search_resp = requests.get(COINGECKO_SEARCH_URL, params={"query": query}, timeout=15)
        search_resp.raise_for_status()
        coins = search_resp.json().get("coins", [])
        if not coins:
            return None
        top = coins[0]
        coin_id = top["id"]

        price_resp = requests.get(
            COINGECKO_PRICE_URL, params={"ids": coin_id, "vs_currencies": "usd"}, timeout=15
        )
        price_resp.raise_for_status()
        price = price_resp.json().get(coin_id, {}).get("usd")
        if price is None:
            return None
        return top.get("name", coin_id), top.get("symbol", "").upper(), price
    except requests.RequestException as e:
        print(f"[price_lookup] crypto lookup failed: {e}")
        return None


def handle_price_query(query: str) -> str:
    query = query.strip()
    if not query:
        return (
            "Usage: <code>/price btc</code> or <code>/price eur/usd</code>\n"
            "Works with most crypto names/symbols and major forex pairs."
        )

    forex_pair = _looks_like_forex(query)
    if forex_pair:
        base, quote = forex_pair
        rate = lookup_forex(base, quote)
        if rate is None:
            return f"Couldn't fetch {base}/{quote} right now. Try again shortly."
        return f"💱 <b>{base}/{quote}</b>: {rate:.4f}"

    result = lookup_crypto(query)
    if result is None:
        return f"Couldn't find a price for \"{query}\". Try a different name or symbol."
    name, symbol, price = result
    price_str = f"${price:,.4f}" if price < 1 else f"${price:,.2f}"
    return f"💰 <b>{name} ({symbol})</b>: {price_str}"
