"""
Listens for incoming messages/commands sent to the bot and replies.
Runs as a long-polling loop — call run_command_loop() in its own thread
(it blocks forever, waiting on Telegram's long-poll).
"""

import json
import os
import time

from telegram_client import get_updates, send_message
from price_lookup import handle_price_query

LAST_UPDATE_ID_FILE = "last_update_id.json"

HELP_TEXT = (
    "👋 <b>Commands</b>\n"
    "/price &lt;name or symbol&gt; — crypto price, e.g. <code>/price btc</code>\n"
    "/price &lt;pair&gt; — forex rate, e.g. <code>/price eur/usd</code>\n"
    "/help — show this message"
)

START_TEXT = (
    "👋 Welcome! This bot posts live news and price alerts to the channel, "
    "and you can DM it commands too.\n\n" + HELP_TEXT
)


def _load_last_update_id():
    if os.path.exists(LAST_UPDATE_ID_FILE):
        try:
            with open(LAST_UPDATE_ID_FILE, "r") as f:
                return json.load(f).get("last_update_id")
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _save_last_update_id(update_id: int):
    with open(LAST_UPDATE_ID_FILE, "w") as f:
        json.dump({"last_update_id": update_id}, f)


def _handle_message(message: dict):
    chat_id = message.get("chat", {}).get("id")
    text = (message.get("text") or "").strip()
    if not chat_id or not text:
        return

    if text.startswith("/start"):
        send_message(START_TEXT, chat_id=chat_id)
    elif text.startswith("/help"):
        send_message(HELP_TEXT, chat_id=chat_id)
    elif text.startswith("/price"):
        query = text[len("/price"):].strip()
        reply = handle_price_query(query)
        send_message(reply, chat_id=chat_id)
    # silently ignore anything else (e.g. regular chatter, unknown commands)


def run_command_loop():
    """Blocks forever, polling for and responding to incoming commands."""
    last_update_id = _load_last_update_id()
    print("[commands] listening for messages...")

    while True:
        offset = (last_update_id + 1) if last_update_id is not None else None
        updates = get_updates(offset=offset, timeout=30)

        for update in updates:
            last_update_id = update["update_id"]
            message = update.get("message") or update.get("channel_post")
            if message:
                try:
                    _handle_message(message)
                except Exception as e:
                    print(f"[commands] error handling message: {e}")

        if updates:
            _save_last_update_id(last_update_id)
        else:
            time.sleep(1)  # brief pause if long-poll returned empty
