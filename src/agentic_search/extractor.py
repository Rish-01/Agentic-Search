from __future__ import annotations

import json

import requests

from .models import ExtractionOutput, ScrapedPage


def _load_google_genai():
    """Lazy import so Ollama-only runs do not require google-genai."""
    try:
        from google import genai
    except ImportError as exc:
        raise ImportError(
            "Gemini requires the `google-genai` package. In the same environment you use to run "
            "this app, run: pip install google-genai"
        ) from exc
    return genai


def _normalize_gemini_model_id(model_name: str) -> str:
    name = model_name.strip()
    if name.startswith("models/"):
        name = name[len("models/") :]
    return name


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _build_prompt(topic: str, pages: list[ScrapedPage], max_chars_per_page: int) -> str:
    page_payload = []
    for page in pages:
        page_payload.append(
            {
                "url": page.url,
                "title": page.title,
                "content": page.markdown[:max_chars_per_page],
            }
        )
    return f"""
You are extracting structured entities for a topic.

Topic: {topic}

Input pages (JSON):
{json.dumps(page_payload, ensure_ascii=True)}

Return ONLY valid JSON with this schema:
{{
  "topic": "string",
  "columns": ["entity_name", "attribute_1", "attribute_2"],
  "entities": [
    {{
      "entity_name": {{
        "value": "string",
        "sources": [{{"url": "https://...", "quote": "short quote from source"}}]
      }},
      "attributes": {{
        "attribute_1": {{
          "value": "string",
          "sources": [{{"url": "https://...", "quote": "short quote from source"}}]
        }}
      }}
    }}
  ]
}}

Rules:
1) Every cell must include at least one source URL.
2) Use only information supported by the provided pages.
3) Keep quotes short and directly evidential.
4) The primary label for each row must be the key "entity_name" exactly (not tool_name or name).
5) URLs must be valid and accessible.
"""


class GeminiExtractor:
    def __init__(self, api_key: str, model_name: str):
        genai = _load_google_genai()
        self._client = genai.Client(api_key=api_key)
        self._model = _normalize_gemini_model_id(model_name)

    def extract(self, topic: str, pages: list[ScrapedPage], max_chars_per_page: int = 8000) -> ExtractionOutput:
        prompt = _build_prompt(topic=topic, pages=pages, max_chars_per_page=max_chars_per_page)
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
        )
        raw = (getattr(response, "text", None) or "").strip()
        text = _strip_json_fence(raw)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Gemini did not return valid JSON. Model={self._model!r}. "
                f"First 500 chars: {text[:500]!r}"
            ) from exc
        return ExtractionOutput.model_validate(parsed)


class OllamaExtractor:
    """Free/local extractor. Requires an Ollama server running locally."""

    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def extract(self, topic: str, pages: list[ScrapedPage], max_chars_per_page: int = 8000) -> ExtractionOutput:
        prompt = _build_prompt(topic=topic, pages=pages, max_chars_per_page=max_chars_per_page)
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "format": "json",
            },
            timeout=120,
        )
        response.raise_for_status()
        text = response.json().get("message", {}).get("content", "")
        text = _strip_json_fence(text)
        parsed = json.loads(text)
        return ExtractionOutput.model_validate(parsed)


def build_extractor(
    provider: str,
    *,
    gemini_api_key: str,
    gemini_model: str,
    ollama_base_url: str,
    ollama_model: str,
):
    if provider == "ollama":
        return OllamaExtractor(base_url=ollama_base_url, model_name=ollama_model)
    if provider == "gemini":
        return GeminiExtractor(api_key=gemini_api_key, model_name=gemini_model)
    raise ValueError(f"Unsupported EXTRACTOR_PROVIDER: {provider}")

