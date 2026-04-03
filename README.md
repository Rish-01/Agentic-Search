# Agentic Search

Web search → page extraction → LLM structuring into an **entity table** where **every cell** carries **source URLs** (and optional quotes).

---

## Live demo

You can find the live demo at [URL](https://agentic-search-cxsyelljdj5jqlnzpguas3.streamlit.app/)

---

## Approach

1. **Search** — Run a text query against the open web using **`ddgs`** (metasearch; no API key). Collect titles, URLs, and snippets.
2. **Scrape** — For the top *N* result URLs, fetch HTML and turn it into **markdown-ish text** with **Trafilatura** (readability-style extraction, no paid scraping API).
3. **Extract** — Send the topic plus a JSON payload of `{url, title, content}` chunks to **Gemini** (default) with a **single structured-output prompt**: return JSON describing `columns`, `entities`, and for each cell a `value` plus `sources[]` with `{url, quote}`.
4. **Validate & present** — **Pydantic** models enforce shape; light **normalization** handles common LLM quirks (e.g. `tool_name` → `entity_name`, null cells). **CLI / API** return JSON; **Streamlit** renders an HTML table so source columns are **clickable links**.

The pipeline is **linear** (no tool-calling loop): simpler to run, easier to cap cost/latency, and good enough when search results already surface relevant pages.

---

## Why these pieces

- **`ddgs`** — Search without signing up for another API; good enough to seed URLs for a demo.
- **`Trafilatura`** — Pulls main text out of HTML so the model isn’t chewing on raw markup.
- **`Gemini`** — Strong instruction-following for 
JSON; One call to turn page text into JSON;
- **`Streamlit`** — Quick UI for the table; hosted demo is just this file on Streamlit Cloud.

There’s also a CLI and a small FastAPI app if you’d rather not use the browser.

---

## Known limitations

- **Coverage:** Only the first *N* search hits are scraped, with a length cap on each page; some sites block fetchers or return thin text.
- **Grounding:** Citations are whatever the model returns with the prompt.
- **Latency:** End-to-end is often slow (network + Gemini); a free Streamlit demo may cold-start after idle.

---

## Setup

**Requirements:** Python **3.10+**, a **[Gemini API key](https://aistudio.google.com/apikey)** when using `EXTRACTOR_PROVIDER=gemini` (default).

From the **repository root** (folder that contains `main.py`):

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set **`GEMINI_API_KEY`**. Optional: **`GEMINI_MODEL`** (must be an id your key supports; see [Gemini models](https://ai.google.dev/gemini-api/docs/models)).

For **Ollama** instead of Gemini: set `EXTRACTOR_PROVIDER=ollama`, run Ollama locally, and `ollama pull` your model.

---

## Run locally

**CLI** (JSON to stdout):

```bash
python main.py --topic "open source database tools"
```

**Streamlit:**

```bash
streamlit run app.py
```

**FastAPI:**

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Example:

```bash
curl -s -X POST http://127.0.0.1:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI startups in healthcare", "search_results": 8, "pages_to_scrape": 5}'
```

**Docker** (API):

```bash
docker build -t agentic-search .
docker run --env-file .env -p 8000:8000 agentic-search
```

---

## Deploy Streamlit (free tier)

1. Fork this repo **GitHub**.
2. [Streamlit Community Cloud](https://streamlit.io/cloud) → **New app** → select repo, branch, main file **`app.py`**.
3. **Settings → Secrets** (TOML), e.g.:

```toml
GEMINI_API_KEY = "your-key-here"
GEMINI_MODEL = "gemini-2.0-flash"
```

`app.py` copies `st.secrets` into `os.environ` so the same config code works as with `.env` locally.

---

## Configuration

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Required when `EXTRACTOR_PROVIDER=gemini` |
| `GEMINI_MODEL` | Model id (e.g. `gemini-2.0-flash`, `gemini-2.5-flash`) |
| `EXTRACTOR_PROVIDER` | `gemini` (default) or `ollama` |
| `SEARCH_PROVIDER` | `duckduckgo` (default) |
| `SCRAPER_PROVIDER` | `trafilatura` (default) |

Do **not** commit `.env` (see `.gitignore`).

---

## Response shape

JSON includes `topic`, `columns`, and `entities`. Each entity has `entity_name` and `attributes`; each field is:

`{ "value": "...", "sources": [ { "url": "...", "quote": "..." } ] }`

---

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| `cannot import name 'genai' from 'google'` | `pip install google-genai` in the active environment |
| Gemini **404 / model not found** | Update `GEMINI_MODEL` to a current id from Google’s docs |
| Import errors for `src.agentic_search` | Run from **repo root**, not inside `src/` |
| Empty or bad scrape | Reduce `pages_to_scrape`; some hosts block fetchers |

---

## Project layout

```
.
├── main.py              # CLI
├── app.py               # Streamlit (+ secrets bridge for Cloud)
├── api.py               # FastAPI
├── Dockerfile
├── requirements.txt
├── .env.example
└── src/agentic_search/  # config, search, scrape, extract, pipeline, models, render
```
