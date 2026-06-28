"""Publish a formatted post to a Telegram channel via the Bot API."""

from html import escape

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

_API = "https://api.telegram.org/bot{token}/sendMessage"
_MAX_LEN = 4096


def _format(body: str, link: str | None) -> str:
    """Escape the LLM body, bold the first line, and append the source link."""
    escaped = escape(body)
    parts = escaped.split("\n", 1)
    title = f"<b>{parts[0]}</b>"
    rest = f"\n{parts[1]}" if len(parts) > 1 else ""
    text = f"{title}{rest}"

    if link:
        safe_link = escape(link, quote=True)
        text += f'\n\n🔗 <a href="{safe_link}">Read more</a>'

    return text[:_MAX_LEN]


def publish(body: str, link: str | None = None) -> bool:
    """Send a single message. Returns True on success."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("[telegram] bot token or channel id is not set.")
        return False

    try:
        resp = requests.post(
            _API.format(token=TELEGRAM_BOT_TOKEN),
            json={
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": _format(body, link),
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=30,
        )
    except requests.RequestException as exc:
        print(f"[telegram] request failed: {exc}")
        return False

    if resp.status_code != 200:
        print(f"[telegram] error {resp.status_code}: {resp.text[:300]}")
        return False

    return True
