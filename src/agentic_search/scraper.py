from __future__ import annotations

import trafilatura

from .models import ScrapedPage, SearchResult


class TrafilaturaScraper:
    """Free/open-source scraper using readability extraction."""

    def scrape_urls(self, results: list[SearchResult], max_pages: int = 5) -> list[ScrapedPage]:
        pages: list[ScrapedPage] = []
        for result in results[:max_pages]:
            try:
                downloaded = trafilatura.fetch_url(result.url)
                extracted = trafilatura.extract(
                    downloaded,
                    include_links=True,
                    output_format="markdown",
                )
            except Exception:
                continue

            if not extracted:
                continue

            pages.append(
                ScrapedPage(
                    url=result.url,
                    title=result.title or None,
                    markdown=extracted,
                    metadata={},
                )
            )
        return pages


def build_scraper(provider: str) -> TrafilaturaScraper:
    if provider == "trafilatura":
        return TrafilaturaScraper()
    raise ValueError(f"Unsupported SCRAPER_PROVIDER: {provider}")

