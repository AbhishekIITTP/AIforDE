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

    # Cap how many items we even try, so a string of failures (rate limits,
    # unfetchable pages) can never turn into hundreds of API calls.
    max_attempts = MAX_POSTS_PER_RUN * 4

    posted = 0
    attempts = 0
    for item in new_items:
        if posted >= MAX_POSTS_PER_RUN or attempts >= max_attempts:
            break

        attempts += 1
        body = summarize(item)
        if not body:
            continue

        if publish(body, item["link"]):
            seen.add(item["id"])
            posted += 1
            print(f"[main] posted: {item['title'][:70]}")
        else:
            print(f"[main] skipped (publish failed): {item['title'][:70]}")

        # Pace requests to stay under Telegram + Groq free-tier rate limits.
        time.sleep(5)

    save_seen(seen)
    print(f"[main] done. {posted} new post(s) published, {attempts} attempt(s).")


if __name__ == "__main__":
    run()
