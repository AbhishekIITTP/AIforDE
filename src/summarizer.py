"""Turn a raw news item into a short, teaching-style Telegram post via Groq."""

import re
import time

import requests

from config import GROQ_API_KEY, GROQ_MODEL
from src.article import fetch_article_text

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _retry_after_seconds(resp: requests.Response) -> float:
    """Seconds to wait after a 429, from headers or the error message."""
    header = resp.headers.get("retry-after")
    if header:
        try:
            return min(float(header), 30.0)
        except ValueError:
            pass
    match = re.search(r"try again in ([\d.]+)s", resp.text)
    if match:
        return min(float(match.group(1)) + 0.5, 30.0)
    return 5.0

_SYSTEM_PROMPT = (
    "You are an expert AI/ML educator writing for data engineers and builders. "
    "You turn a single news item into a SHORT, engaging Telegram post that both "
    "summarizes and teaches in very simple English. No hype, no jargon.\n\n"
    "Use exactly this structure (plain text, no markdown headings, no links):\n"
    "Line 1: a punchy title (max 8 words) with one leading emoji.\n"
    "Line 2: one flowing simple sentence that explains what happened (the gist).\n"
    "Then 2-4 bullet lines, each starting with '• ', explaining the key points "
    "in plain words a beginner understands.\n"
    "Then one line starting with '🛠 For data engineers: ' explaining why it "
    "matters in real data/ML work.\n"
    "End with one line starting with '📚 Learn: ' giving a tiny concrete next step.\n"
    "Keep the whole post under 130 words. Do NOT include URLs."
)


def _clean_feed_noise(text: str) -> str:
    """Drop boilerplate lines common in HN/RSS summaries."""
    bad = ("article url", "comments url", "points:", "# comments")
    kept = [
        line.strip()
        for line in text.replace(". ", ".\n").splitlines()
        if line.strip() and not any(b in line.lower() for b in bad)
    ]
    return " ".join(kept)


def _fallback_post(item: dict) -> str:
    """A readable bullet-style post used when no Groq key is set."""
    clean = _clean_feed_noise(item["summary"]).strip()
    lines = [f"🧠 {item['title']}"]

    if clean:
        # First sentence as a flowing intro, next ones as bullets.
        sentences = [s.strip() for s in clean.split(". ") if s.strip()]
        if sentences:
            lines.append(f"\n{sentences[0].rstrip('.')}.")
        for s in sentences[1:3]:
            lines.append(f"• {s.rstrip('.')}")

    lines.append("\n🛠 For data engineers: a fresh AI/ML update worth a look.")
    lines.append("📚 Learn: open the link for the full details.")
    return "\n".join(lines)


def summarize(item: dict) -> str | None:
    """Return a ready-to-post text body, or None on failure.

    Falls back to a simple formatted post when GROQ_API_KEY is not configured,
    so the Telegram pipeline can be tested before adding an LLM key.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        print("[summarizer] no Groq key set — using basic fallback post.")
        return _fallback_post(item)

    # Prefer the real article text; fall back to the (often thin) feed summary.
    article = fetch_article_text(item["link"])
    content = article if len(article) > len(item["summary"]) else item["summary"]

    # Keep content modest so we stay well under Groq's free-tier TPM limit.
    user_content = (
        f"Title: {item['title']}\n\n"
        f"Source: {item['source']}\n\n"
        f"Content: {content[:1800]}"
    )

    payload = {
        "model": GROQ_MODEL,
        "temperature": 0.5,
        "max_tokens": 300,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    # Retry a few times on rate limits (HTTP 429), honoring the suggested wait.
    # On any Groq failure we fall back to a feed-based post rather than dropping
    # the item, so a throttled LLM never turns into a run that posts nothing.
    for attempt in range(3):
        try:
            resp = requests.post(_GROQ_URL, headers=headers, json=payload, timeout=60)
        except requests.RequestException as exc:
            print(f"[summarizer] request failed: {exc} — using fallback.")
            return _fallback_post(item)

        if resp.status_code == 429:
            wait = _retry_after_seconds(resp)
            print(f"[summarizer] rate limited; waiting {wait:.1f}s (attempt {attempt + 1}/3)")
            time.sleep(wait)
            continue

        if resp.status_code != 200:
            print(f"[summarizer] Groq error {resp.status_code}: {resp.text[:300]} — using fallback.")
            return _fallback_post(item)

        try:
            body = resp.json()["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, ValueError) as exc:
            print(f"[summarizer] unexpected response: {exc} — using fallback.")
            return _fallback_post(item)

        return body or _fallback_post(item)

    print("[summarizer] repeated rate limits — using fallback post.")
    return _fallback_post(item)
