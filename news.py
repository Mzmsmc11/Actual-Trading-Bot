"""
Fetches RSS feeds, filters out stories already posted, formats new ones.
"""

import json
import os
import feedparser
from config import RSS_FEEDS, SEEN_LINKS_FILE

MAX_SEEN_LINKS = 2000


def _load_seen() -> set:
    if os.path.exists(SEEN_LINKS_FILE):
        try:
            with open(SEEN_LINKS_FILE, "r") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, OSError):
            return set()
    return set()


def _save_seen(seen: set) -> None:
    trimmed = list(seen)[-MAX_SEEN_LINKS:]
    with open(SEEN_LINKS_FILE, "w") as f:
        json.dump(trimmed, f)


def fetch_new_stories() -> list:
    seen = _load_seen()
    new_stories = []

    for label, url in RSS_FEEDS:
        try:
            parsed = feedparser.parse(url)
        except Exception as e:
            print(f"[news] failed to parse {label}: {e}")
            continue

        if parsed.bozo and not parsed.entries:
            print(f"[news] {label} returned no usable entries (feed may have moved)")
            continue

        for entry in parsed.entries[:15]:
            link = entry.get("link")
            if not link or link in seen:
                continue
            seen.add(link)
            new_stories.append(
                {
                    "source": label,
                    "title": entry.get("title", "(no title)").strip(),
                    "link": link,
                }
            )

    _save_seen(seen)
    return new_stories


def format_story(story: dict) -> str:
    return f"🗞 <b>{story['source']}</b>\n{story['title']}\n{story['link']}"
