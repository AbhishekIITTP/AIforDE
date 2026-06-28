"""AI News Agent — entry point.

Pipeline: fetch feeds -> filter new items -> summarize with Groq -> post to Telegram.
Run with:  python main.py
"""

import time

from config import MAX_POSTS_PER_RUN
from src.sources import fetch_items
from src.state import load_seen, save_seen
from src.summarizer import summarize
from src.telegram_publisher import publish


def run() -> None:
    seen = load_seen()
    items = fetch_items()
    new_items = [it for it in items if it["id"] not in seen]

    print(f"[main] {len(items)} relevant items fetched, {len(new_items)} new.")

    posted = 0
    for item in new_items:
        if posted >= MAX_POSTS_PER_RUN:
            break

        body = summarize(item)
        if not body:
            continue

        if publish(body, item["link"]):
            seen.add(item["id"])
            posted += 1
            print(f"[main] posted: {item['title'][:70]}")
            time.sleep(3)  # gentle pacing to respect Telegram rate limits
        else:
            print(f"[main] skipped (publish failed): {item['title'][:70]}")

    save_seen(seen)
    print(f"[main] done. {posted} new post(s) published.")


if __name__ == "__main__":
    run()
