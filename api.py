from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.agentic_search.pipeline import AgenticSearchPipeline

app = FastAPI(title="Agentic Search API", version="0.1.0")


class ExtractRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Topic query for entity extraction.")
    search_results: int = Field(default=8, ge=3, le=20)
    pages_to_scrape: int = Field(default=5, ge=2, le=15)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract")
def extract(payload: ExtractRequest) -> dict:
    pipeline = AgenticSearchPipeline()
    output = pipeline.run(
        topic=payload.topic,
        search_results=payload.search_results,
        pages_to_scrape=payload.pages_to_scrape,
    )
    return output.model_dump()

