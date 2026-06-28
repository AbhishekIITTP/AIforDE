"""Dry run: fetch and preview the items the agent WOULD post.

No API keys needed. Nothing is sent to Telegram or Groq.
Run with:  python dry_run.py
"""

from src.sources import fetch_items

LIMIT = 15


def main() -> None:
    items = fetch_items()
    print(f"\nFetched {len(items)} relevant AI/ML/data items.")
    print(f"Showing first {min(LIMIT, len(items))}:\n")
    for i, item in enumerate(items[:LIMIT], start=1):
        print(f"{i:>2}. {item['title']}")
        print(f"    source: {item['source']}")
        print(f"    link:   {item['link']}")
        snippet = item["summary"][:160].strip()
        if snippet:
            print(f"    about:  {snippet}...")
        print()


if __name__ == "__main__":
    main()
