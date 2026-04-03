# Agentic Search

Given a topic (e.g. “open source database tools”), the app searches the web, scrapes pages, and uses an LLM to return a **table of entities** with **per-cell source URLs**. You can use the **CLI**, **Streamlit UI**, or **HTTP API**.

**Requirements:** Python **3.10+**, a **[Gemini API key](https://aistudio.google.com/apikey)** (default setup).

---

## Quick start

From the **repository root** (the folder that contains `main.py`):

```bash
git clone <your-repo-url>
cd Agentic-Search

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set **`GEMINI_API_KEY`**. Optional: change **`GEMINI_MODEL`** (see [Gemini models](https://ai.google.dev/gemini-api/docs/models)).

Default `.env` uses **Gemini** for extraction. To use **Ollama** instead, set `EXTRACTOR_PROVIDER=ollama` and run Ollama locally with your chosen model pulled.

---

## Run

**CLI** (prints JSON to the terminal):

```bash
python main.py --topic "open source database tools"
```

**Streamlit** (browser UI):

```bash
streamlit run app.py
```

**HTTP API** (FastAPI):

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Example request:

```bash
curl -s -X POST http://127.0.0.1:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI startups in healthcare", "search_results": 8, "pages_to_scrape": 5}'
```

**Docker** (API only):

```bash
docker build -t agentic-search .
docker run --env-file .env -p 8000:8000 agentic-search
```

---

## Configuration

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Required when `EXTRACTOR_PROVIDER=gemini` |
| `GEMINI_MODEL` | e.g. `gemini-2.5-flash` (must match an id your key can use) |
| `EXTRACTOR_PROVIDER` | `gemini` (default) or `ollama` |
| `SEARCH_PROVIDER` | `duckduckgo` (default) |
| `SCRAPER_PROVIDER` | `trafilatura` (default) |

Copy from `.env.example` and adjust. **Do not commit `.env`** (it is gitignored).

---

## Response shape

JSON includes `topic`, `columns`, and `entities`. Each row has `entity_name` and `attributes`; each field is `{ "value": "...", "sources": [ { "url": "...", "quote": "..." } ] }` so values stay traceable to URLs.

---

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| `cannot import name 'genai' from 'google'` | In the same venv: `pip install google-genai` |
| Gemini **404 / model not found** | Update `GEMINI_MODEL` in `.env` to a current model id from Google’s docs |
| Import errors for `src.agentic_search` | Run commands from the **repo root**, not inside `src/` |
| Search/scrape failures | Some sites block scrapers; fewer `pages_to_scrape` may help |

---

## Project layout

```
.
├── main.py              # CLI
├── app.py               # Streamlit
├── api.py               # FastAPI
├── Dockerfile
├── requirements.txt
├── .env.example
└── src/agentic_search/  # pipeline: search → scrape → extract
```