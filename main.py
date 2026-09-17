"""
Entry point. Runs everything together, in one process:
  1. News job (scheduled)  -> posts new stories to the channel
  2. Price job (scheduled) -> posts move alerts + periodic snapshot to the channel
  3. Command loop (always on) -> replies to /start, /help, /price from DMs

Run with:  python main.py
Stop with: Ctrl+C
"""

import time
import traceback
from apscheduler.schedulers.background import BackgroundScheduler

from config import NEWS_CHECK_INTERVAL, PRICE_CHECK_INTERVAL, CHANNEL_ID
from telegram_client import send_message
from news import fetch_new_stories, format_story
from prices import get_crypto_prices, get_forex_rates, check_for_moves, build_price_snapshot
from commands import run_command_loop

SNAPSHOT_EVERY_N_CYCLES = max(1, 3600 // PRICE_CHECK_INTERVAL)
_price_cycle_count = 0


def job_check_news():
    if not CHANNEL_ID:
        return  # no channel configured yet - skip quietly
    try:
        stories = fetch_new_stories()
        for story in stories:
            send_message(format_story(story))
            time.sleep(1)
        if stories:
            print(f"[news] posted {len(stories)} new stories")
    except Exception:
        print("[news] job failed:")
        traceback.print_exc()


def job_check_prices():
    global _price_cycle_count
    if not CHANNEL_ID:
        return  # no channel configured yet - skip quietly
    try:
        crypto = get_crypto_prices()
        forex = get_forex_rates()

        alerts = check_for_moves(crypto, forex)
        for alert in alerts:
            send_message(alert)
            time.sleep(1)
        if alerts:
            print(f"[prices] posted {len(alerts)} alerts")

        _price_cycle_count += 1
        if _price_cycle_count >= SNAPSHOT_EVERY_N_CYCLES:
            _price_cycle_count = 0
            send_message(build_price_snapshot(crypto, forex))
            print("[prices] posted snapshot")
    except Exception:
        print("[prices] job failed:")
        traceback.print_exc()


def main():
    print("Starting bot...")
    if not CHANNEL_ID:
        print("NOTE: CHANNEL_ID is not set - channel posting is paused, "
              "but /price DM commands will still work.")
    print(f"News checked every {NEWS_CHECK_INTERVAL}s, prices every {PRICE_CHECK_INTERVAL}s")

    scheduler = BackgroundScheduler()
    scheduler.add_job(job_check_news, "interval", seconds=NEWS_CHECK_INTERVAL)
    scheduler.add_job(job_check_prices, "interval", seconds=PRICE_CHECK_INTERVAL)
    scheduler.start()

    job_check_news()
    job_check_prices()

    try:
        run_command_loop()  # blocks the main thread forever
    except (KeyboardInterrupt, SystemExit):
        print("Stopping bot.")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
