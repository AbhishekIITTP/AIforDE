"""Fetch and filter news items from free RSS/Atom feeds."""

import hashlib
import re
from html import unescape

import feedparser

from config import FEEDS, KEYWORDS

_TAG_RE = re.compile(r"<[^>]+>")

# Whole-word matcher so "ai" does not match "California", "ml" not "html", etc.
_KEYWORD_RE = re.compile(
    r"\b(" + "|".join(re.escape(kw) for kw in KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    """Strip HTML tags and collapse whitespace from a feed field."""
    if not text:
        return ""
    text = _TAG_RE.sub(" ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _is_relevant(title: str, summary: str) -> bool:
    # Match keywords against the title only — feed summaries are noisy and
    # often contain comment URLs / boilerplate that trigger false positives.
    return bool(_KEYWORD_RE.search(title))


def _make_id(link: str, title: str) -> str:
    """Stable id used for de-duplication across runs."""
    raw = (link or title).strip().lower()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def fetch_items() -> list[dict]:
    """Return a de-duplicated, relevance-filtered list of news items.

    Each item is a dict: {id, title, summary, link, source}.
    """
    items: dict[str, dict] = {}

    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception as exc:  # network / parse error on one feed is non-fatal
            print(f"[sources] failed to parse {url}: {exc}")
            continue

        source = _clean(getattr(feed.feed, "title", "")) or url
        for entry in feed.entries:
            title = _clean(entry.get("title", ""))
            summary = _clean(entry.get("summary", "") or entry.get("description", ""))
            link = entry.get("link", "")
            if not title or not link:
                continue
            if not _is_relevant(title, summary):
                continue

            item_id = _make_id(link, title)
            # First occurrence wins (avoids cross-feed duplicates).
            items.setdefault(
                item_id,
                {
                    "id": item_id,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "source": source,
                },
            )

    return list(items.values())
