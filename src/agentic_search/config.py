from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    search_provider: str = "duckduckgo"
    scraper_provider: str = "trafilatura"
    extractor_provider: str = "gemini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"


def get_settings() -> Settings:
    load_dotenv()
    search_provider = os.getenv("SEARCH_PROVIDER", "duckduckgo")
    scraper_provider = os.getenv("SCRAPER_PROVIDER", "trafilatura")
    extractor_provider = os.getenv("EXTRACTOR_PROVIDER", "gemini")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    allowed_search = {"duckduckgo"}
    allowed_scraper = {"trafilatura"}
    allowed_extractor = {"gemini", "ollama"}
    if search_provider not in allowed_search:
        raise ValueError(f"Unsupported SEARCH_PROVIDER={search_provider}")
    if scraper_provider not in allowed_scraper:
        raise ValueError(f"Unsupported SCRAPER_PROVIDER={scraper_provider}")
    if extractor_provider not in allowed_extractor:
        raise ValueError(f"Unsupported EXTRACTOR_PROVIDER={extractor_provider}")

    if extractor_provider == "gemini" and not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required when EXTRACTOR_PROVIDER=gemini")

    return Settings(
        search_provider=search_provider,
        scraper_provider=scraper_provider,
        extractor_provider=extractor_provider,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
    )

