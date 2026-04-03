from __future__ import annotations

import json

import streamlit as st

from src.agentic_search.pipeline import AgenticSearchPipeline
from src.agentic_search.render import flat_rows_to_html_table, to_flat_rows

st.set_page_config(page_title="Agentic Search", layout="wide")
st.title("Agentic Search")
st.caption("DuckDuckGo -> Trafilatura -> Ollama/Gemini -> Source-traceable table")

topic = st.text_input(
    "Topic query",
    placeholder="AI startups in healthcare",
)
col1, col2 = st.columns(2)
with col1:
    search_results = st.slider("Search results", 3, 15, 8)
with col2:
    pages_to_scrape = st.slider("Pages to scrape", 2, 10, 5)

if st.button("Run extraction", type="primary"):
    if not topic.strip():
        st.warning("Please enter a topic query.")
    else:
        with st.spinner("Running pipeline..."):
            try:
                pipeline = AgenticSearchPipeline()
                output = pipeline.run(
                    topic=topic.strip(),
                    search_results=search_results,
                    pages_to_scrape=pages_to_scrape,
                )
            except Exception as exc:
                st.error(f"Pipeline failed: {exc}")
            else:
                st.subheader("Structured Table")
                rows = to_flat_rows(output)
                st.markdown(
                    """
<style>
.agentic-table-wrap { overflow-x: auto; margin-bottom: 1rem; }
.agentic-table-wrap table th,
.agentic-table-wrap table td {
    border: 1px solid rgba(128, 128, 128, 0.35);
    padding: 0.35rem 0.55rem;
    vertical-align: top;
    text-align: left;
}
.agentic-table-wrap table th { font-weight: 600; }
.agentic-table-wrap a { text-decoration: underline; }
</style>
""",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="agentic-table-wrap">{flat_rows_to_html_table(rows)}</div>',
                    unsafe_allow_html=True,
                )

                st.subheader("Raw JSON Output")
                st.code(json.dumps(output.model_dump(), indent=2), language="json")
