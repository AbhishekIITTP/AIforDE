"""Persist which items have already been posted (de-duplication across runs)."""

import json
import os

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_SEEN_FILE = os.path.join(_DATA_DIR, "seen.json")

# Cap stored ids so the file never grows without bound.
_MAX_SEEN = 2000


def load_seen() -> set[str]:
    if not os.path.exists(_SEEN_FILE):
        return set()
    try:
        with open(_SEEN_FILE, "r", encoding="utf-8") as fh:
            return set(json.load(fh))
    except (ValueError, OSError) as exc:
        print(f"[state] could not read seen file: {exc}")
        return set()


def save_seen(seen: set[str]) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    # Keep only the most recent ids (sets are unordered, so just trim).
    trimmed = list(seen)[-_MAX_SEEN:]
    with open(_SEEN_FILE, "w", encoding="utf-8") as fh:
        json.dump(trimmed, fh, indent=2)
