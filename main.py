from __future__ import annotations

import argparse
import json

from src.agentic_search.pipeline import AgenticSearchPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agentic Search challenge boilerplate CLI")
    parser.add_argument("--topic", required=True, help="Topic query to search and extract entities for.")
    parser.add_argument("--search-results", type=int, default=8, help="Number of search results to fetch.")
    parser.add_argument("--pages-to-scrape", type=int, default=5, help="Number of pages to scrape.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = AgenticSearchPipeline()
    output = pipeline.run(
        topic=args.topic,
        search_results=args.search_results,
        pages_to_scrape=args.pages_to_scrape,
    )
    print(json.dumps(output.model_dump(), indent=2))


if __name__ == "__main__":
    main()

