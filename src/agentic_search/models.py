from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str | None = None
    score: float | None = None


class ScrapedPage(BaseModel):
    url: str
    title: str | None = None
    markdown: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceRef(BaseModel):
    url: str
    quote: str | None = None


class CellValue(BaseModel):
    value: str = ""
    sources: list[SourceRef] = Field(default_factory=list)

    @field_validator("value", mode="before")
    @classmethod
    def coerce_value(cls, v: object) -> str:
        if v is None:
            return ""
        if isinstance(v, str):
            return v
        if isinstance(v, (int, float, bool)):
            return str(v)
        return str(v)


_ENTITY_NAME_ALIASES = ("tool_name", "name", "product_name", "company_name", "title")


class EntityRecord(BaseModel):
    entity_name: CellValue
    attributes: dict[str, CellValue] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_entity_row(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        if "entity_name" not in d:
            for key in _ENTITY_NAME_ALIASES:
                if key in d:
                    d["entity_name"] = d.pop(key)
                    break
        if d.get("entity_name") is None:
            d["entity_name"] = {"value": "", "sources": []}
        attrs = d.get("attributes")
        if attrs is None:
            d["attributes"] = {}
        elif isinstance(attrs, dict):
            empty: dict[str, object] = {"value": "", "sources": []}
            d["attributes"] = {k: empty if v is None else v for k, v in attrs.items()}
        return d


class ExtractionOutput(BaseModel):
    topic: str
    columns: list[str]
    entities: list[EntityRecord]

