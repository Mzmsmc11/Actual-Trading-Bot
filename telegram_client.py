"""
Minimal Telegram Bot API client (plain HTTP, no heavy framework needed).
"""

import requests
from config import BOT_TOKEN, CHANNEL_ID

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(text: str, chat_id: str = None, disable_preview: bool = False) -> bool:
    """
    Send a message. Defaults to the configured channel (CHANNEL_ID); pass
    chat_id to reply to a specific user/DM instead (used for /price replies).
    """
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN must be set (see .env.example).")
    target = chat_id or CHANNEL_ID
    if not target:
        print("[telegram] no chat_id/CHANNEL_ID set, skipping send")
        return False

    url = f"{API_BASE}/sendMessage"
    payload = {
        "chat_id": target,
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


def get_updates(offset: int = None, timeout: int = 30) -> list:
    """
    Long-poll Telegram for new incoming messages/commands sent to the bot.
    `offset` should be the last processed update_id + 1.
    Returns a list of update dicts (empty list on timeout/error).
    """
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN must be set (see .env.example).")

    url = f"{API_BASE}/getUpdates"
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset

    try:
        resp = requests.get(url, params=params, timeout=timeout + 10)
        resp.raise_for_status()
        return resp.json().get("result", [])
    except requests.RequestException as e:
        print(f"[telegram] get_updates failed: {e}")
        return []
