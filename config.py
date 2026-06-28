"""Central configuration for the AI News Agent.

All secrets are read from environment variables (loaded from a local .env
file when present). Feed list and keyword filters can be tuned freely.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str = "") -> str:
    """Return an env var, treating empty/whitespace values as unset.

    GitHub Actions passes unset secrets as empty strings, so we fall back
    to the default instead of breaking on blank values.
    """
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default


# ----- Groq (free LLM inference) -----
GROQ_API_KEY = _env("GROQ_API_KEY")
GROQ_MODEL = _env("GROQ_MODEL", "llama-3.1-8b-instant")

# ----- Telegram -----
TELEGRAM_BOT_TOKEN = _env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = _env("TELEGRAM_CHANNEL_ID")

# ----- Behaviour -----
MAX_POSTS_PER_RUN = int(_env("MAX_POSTS_PER_RUN", "3"))

# RSS / Atom sources. All free, no API key required.
# Add or remove freely — the agent filters them by KEYWORDS below.
FEEDS = [
    "http://export.arxiv.org/rss/cs.AI",        # arXiv – Artificial Intelligence
    "http://export.arxiv.org/rss/cs.LG",        # arXiv – Machine Learning
    "http://export.arxiv.org/rss/cs.CL",        # arXiv – Computation & Language (NLP/LLMs)
    "https://hnrss.org/frontpage",              # Hacker News front page
    "https://huggingface.co/blog/feed.xml",     # Hugging Face blog
    "https://blog.google/technology/ai/rss/",   # Google AI blog
    "https://bair.berkeley.edu/blog/feed.xml",  # Berkeley AI Research
]

# Only keep items whose title/summary mentions one of these (case-insensitive).
# Keeps the channel focused on AI / ML / data topics.
KEYWORDS = [
    "ai", "ml", "llm", "agent", "agents", "agentic", "model", "models", "gpt",
    "data", "pipeline", "rag", "vector", "transformer", "neural", "diffusion",
    "machine learning", "deep learning", "embedding", "fine-tun", "inference",
    "dataset", "prompt", "openai", "anthropic", "hugging face", "mlops",
    "claude", "gemini", "mistral", "llama", "nlp", "fine-tuning",
]
