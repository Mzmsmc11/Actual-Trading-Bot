"""
Entry point. Runs two recurring jobs forever:
  1. Poll news feeds -> post any new stories
  2. Poll prices -> post alerts on big moves (+ an hourly snapshot)

Run with:  python main.py
Stop with: Ctrl+C
"""

import time
import traceback
from apscheduler.schedulers.blocking import BlockingScheduler

from config import NEWS_CHECK_INTERVAL, PRICE_CHECK_INTERVAL
from telegram_client import send_message
from news import fetch_new_stories, format_story
from prices import get_crypto_prices, get_forex_rates, check_for_moves, build_price_snapshot

# how many price-check cycles between full snapshots (e.g. 12 cycles * 5min = hourly)
SNAPSHOT_EVERY_N_CYCLES = max(1, 3600 // PRICE_CHECK_INTERVAL)
_price_cycle_count = 0


def job_check_news():
    try:
        stories = fetch_new_stories()
        for story in stories:
            send_message(format_story(story), disable_preview=False)
            time.sleep(1)  # avoid hammering Telegram's rate limit
        if stories:
            print(f"[news] posted {len(stories)} new stories")
    except Exception:
        print("[news] job failed:")
        traceback.print_exc()


def job_check_prices():
    global _price_cycle_count
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
    print(f"News checked every {NEWS_CHECK_INTERVAL}s, prices every {PRICE_CHECK_INTERVAL}s")

    scheduler = BlockingScheduler()
    scheduler.add_job(job_check_news, "interval", seconds=NEWS_CHECK_INTERVAL, next_run_time=None)
    scheduler.add_job(job_check_prices, "interval", seconds=PRICE_CHECK_INTERVAL, next_run_time=None)

    # Run once immediately on startup, then let the scheduler take over
    job_check_news()
    job_check_prices()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Stopping bot.")


if __name__ == "__main__":
    main()
