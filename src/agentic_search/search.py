from __future__ import annotations

from ddgs import DDGS

from .models import SearchResult


class DuckDuckGoSearcher:
    """Free search provider with no API key requirements (via ddgs metasearch)."""

    def search(self, topic: str, max_results: int = 8) -> list[SearchResult]:
        results = []
        raw_results = DDGS().text(topic, max_results=max_results)
        for item in raw_results:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("href", ""),
                    snippet=item.get("body"),
                    score=None,
                )
            )
        return results


def build_searcher(provider: str) -> DuckDuckGoSearcher:
    if provider == "duckduckgo":
        return DuckDuckGoSearcher()
    raise ValueError(f"Unsupported SEARCH_PROVIDER: {provider}")

