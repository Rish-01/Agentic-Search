from __future__ import annotations

from .config import get_settings
from .extractor import build_extractor
from .models import ExtractionOutput
from .scraper import build_scraper
from .search import build_searcher


class AgenticSearchPipeline:
    def __init__(self):
        settings = get_settings()
        self.searcher = build_searcher(settings.search_provider)
        self.scraper = build_scraper(settings.scraper_provider)
        self.extractor = build_extractor(
            settings.extractor_provider,
            gemini_api_key=settings.gemini_api_key,
            gemini_model=settings.gemini_model,
            ollama_base_url=settings.ollama_base_url,
            ollama_model=settings.ollama_model,
        )

    def run(self, topic: str, search_results: int = 8, pages_to_scrape: int = 5) -> ExtractionOutput:
        results = self.searcher.search(topic=topic, max_results=search_results)
        pages = self.scraper.scrape_urls(results=results, max_pages=pages_to_scrape)
        return self.extractor.extract(topic=topic, pages=pages)

