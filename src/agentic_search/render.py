from __future__ import annotations

import html

from .models import ExtractionOutput


def to_flat_rows(data: ExtractionOutput) -> list[dict]:
    rows: list[dict] = []
    for entity in data.entities:
        row: dict = {
            "entity_name": entity.entity_name.value,
            "entity_name_sources": ", ".join(src.url for src in entity.entity_name.sources),
        }
        for col in data.columns:
            if col == "entity_name":
                continue
            cell = entity.attributes.get(col)
            row[col] = cell.value if cell else ""
            row[f"{col}_sources"] = ", ".join(src.url for src in (cell.sources if cell else []))
        rows.append(row)
    return rows


def flat_rows_to_html_table(rows: list[dict]) -> str:
    """HTML table for Streamlit: *_sources columns become clickable links ([1], [2], …)."""
    if not rows:
        return "<p><em>No rows.</em></p>"

    keys = list(rows[0].keys())

    def cell_inner(key: str, value: object) -> str:
        text = "" if value is None else str(value)
        if key.endswith("_sources") and text.strip():
            links: list[str] = []
            for i, raw in enumerate(text.split(", "), 1):
                url = raw.strip()
                if not url:
                    continue
                safe = html.escape(url, quote=True)
                links.append(
                    f'<a href="{safe}" target="_blank" rel="noopener noreferrer">[{i}]</a>'
                )
            return " ".join(links) if links else ""
        return html.escape(text)

    header = "".join(f"<th>{html.escape(k)}</th>" for k in keys)
    body_rows: list[str] = []
    for row in rows:
        cells = "".join(f"<td>{cell_inner(k, row.get(k))}</td>" for k in keys)
        body_rows.append(f"<tr>{cells}</tr>")

    return (
        '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">'
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
    )
