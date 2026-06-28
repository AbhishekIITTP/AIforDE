"""Fetch the readable main text of an article URL (free, no API).

Many feeds (Hacker News especially) only provide a title and boilerplate.
Pulling the real page text lets the summarizer write specific, useful bullets
instead of vague generalities.
"""

import trafilatura

# Skip extraction for link types that have no useful article body.
_SKIP_HINTS = (
    "news.ycombinator.com/item",
    "youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    ".pdf",
)

_MAX_CHARS = 4000


def fetch_article_text(url: str) -> str:
    """Return cleaned article text, or "" if it can't be extracted."""
    if not url or any(h in url.lower() for h in _SKIP_HINTS):
        return ""

    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False,
        )
    except Exception as exc:  # network / parse issues are non-fatal
        print(f"[article] could not fetch {url}: {exc}")
        return ""

    if not text:
        return ""
    return text.strip()[:_MAX_CHARS]
