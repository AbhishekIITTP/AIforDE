# AI News Agent 🤖📰

An autonomous agent that watches the AI/ML world, writes **short, teaching-style
summaries** with a **data-engineer angle**, and posts them to your **Telegram
channel** — all on **100% free** tools.

```
RSS feeds ──> filter (AI/ML/data) ──> Groq LLM summarize+teach ──> Telegram channel
                                              │
                                     de-dup state (seen.json)
```

## What it does

- Pulls fresh items from free feeds (arXiv, Hacker News, Hugging Face, Google AI, BAIR).
- Keeps only AI / ML / data topics (keyword filter you can edit in `config.py`).
- Uses **Groq** (free, fast LLM API) to write a compact post:
  punchy title → what it is → **🛠 why it matters for data engineers** → **📚 learn next step**.
- Posts to your Telegram channel and never repeats an item.

## Cost: ₹0

| Piece | Service | Cost |
|-------|---------|------|
| LLM | [Groq](https://console.groq.com) | Free tier |
| Sources | Public RSS | Free |
| Publishing | Telegram Bot API | Free |
| Scheduling | GitHub Actions | Free |

---

## 1. Get your free keys

**Groq API key**
1. Sign up at <https://console.groq.com>.
2. Create a key at <https://console.groq.com/keys>.

**Telegram bot + channel**
1. In Telegram, open **@BotFather** → `/newbot` → copy the **bot token**.
2. Create (or open) your channel.
3. Add the bot as an **Admin** of the channel (with "Post messages" permission).
4. Your `TELEGRAM_CHANNEL_ID` is the public `@username`, or a numeric `-100...` id for private channels.

---

## 2. Run locally (test it)

```powershell
# from the project folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# create your .env from the template, then fill in the values
Copy-Item .env.example .env
notepad .env

python main.py
```

You should see logs and new posts appear in your channel.

> Tip: set `MAX_POSTS_PER_RUN=2` while testing so you don't flood the channel.

---

## 3. Run automatically for free (GitHub Actions)

1. Push this folder to a GitHub repo.
2. In the repo: **Settings → Secrets and variables → Actions → New repository secret**, add:
   - `GROQ_API_KEY`
   - `GROQ_MODEL` (e.g. `llama-3.3-70b-versatile`)
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHANNEL_ID`
   - `MAX_POSTS_PER_RUN` (e.g. `5`)
3. The workflow in `.github/workflows/run.yml` runs every 6 hours and can be
   triggered manually from the **Actions** tab.

The agent commits `data/seen.json` back to the repo so it remembers what it
already posted between runs.

---

## Customize

- **Sources / topics:** edit `FEEDS` and `KEYWORDS` in `config.py`.
- **Voice & format:** edit the prompt in `src/summarizer.py`.
- **Frequency:** change the `cron` in `.github/workflows/run.yml`.

## Project layout

```
ai-news-agent/
├── main.py                 # orchestrates the pipeline
├── config.py               # feeds, keywords, env config
├── requirements.txt
├── .env.example
├── src/
│   ├── sources.py          # fetch + filter feeds
│   ├── summarizer.py       # Groq LLM summarize & teach
│   ├── telegram_publisher.py
│   └── state.py            # de-duplication
└── .github/workflows/run.yml
```

## Roadmap ideas (your monetization funnel)

- Add a **LinkedIn** publisher (reuse the same summary body).
- Add a "deep-dive" weekly post for a **paid tier**.
- Self-host a static site that archives every post for SEO.
