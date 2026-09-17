"""
Minimal Telegram Bot API client. We use plain HTTP requests instead of a heavy
library since all we need is "send a message to my channel."
"""

import requests
from config import BOT_TOKEN, CHANNEL_ID

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(text: str, disable_preview: bool = False) -> bool:
    """Send a message to the configured channel. Returns True on success."""
    if not BOT_TOKEN or not CHANNEL_ID:
        raise RuntimeError(
            "BOT_TOKEN and CHANNEL_ID must be set (see .env.example)."
        )

    url = f"{API_BASE}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": disable_preview,
    }
    try:
        resp = requests.post(url, data=payload, timeout=15)
        if resp.status_code != 200:
            print(f"[telegram] send failed: {resp.status_code} {resp.text}")
            return False
        return True
    except requests.RequestException as e:
        print(f"[telegram] request error: {e}")
        return False
