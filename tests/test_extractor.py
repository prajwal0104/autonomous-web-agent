"""Unit tests for DataExtractor and structured content utilities."""

import pytest
from src.tools.extractor import DataExtractor


SAMPLE_HTML_WITH_TABLE_AND_LINKS = """
<!DOCTYPE html>
<html>
<head><title>Research Catalog</title></head>
<body>
    <h1>Top AI Models 2026</h1>
    <h2>Benchmark Overview</h2>
    <p>Below is a summary of current frontier architectures.</p>
    <table>
        <thead>
            <tr><th>Model</th><th>Architecture</th><th>Context Window</th></tr>
        </thead>
        <tbody>
            <tr><td>Gemini 2.5</td><td>Sparse MoE</td><td>2M tokens</td></tr>
            <tr><td>GPT-5o</td><td>Dense Transformer</td><td>128k tokens</td></tr>
            <tr><td>Claude 3.7</td><td>Hybrid SSM</td><td>1M tokens</td></tr>
        </tbody>
    </table>
    <h2>Useful References</h2>
    <ul>
        <li><a href="/docs/guide.html">Documentation Guide</a></li>
        <li><a href="https://example.com/external-paper">External Research Paper</a></li>
        <li><a href="javascript:void(0)">Invalid Script Link</a></li>
        <li><a href="">Empty Link</a></li>
        <li><a href="/api/v1/endpoints">API Endpoints</a></li>
    </ul>
</body>
</html>
"""


def test_extract_tables_success():
    """Verify HTML table rows and cells are parsed into structured 2D lists."""
    tables = DataExtractor.extract_tables(SAMPLE_HTML_WITH_TABLE_AND_LINKS)
    assert len(tables) == 1
    table = tables[0]
    # 1 header row + 3 data rows = 4 rows
    assert len(table) == 4
    assert table[0] == ["Model", "Architecture", "Context Window"]
    assert table[1] == ["Gemini 2.5", "Sparse MoE", "2M tokens"]
    assert table[2] == ["GPT-5o", "Dense Transformer", "128k tokens"]
    assert table[3] == ["Claude 3.7", "Hybrid SSM", "1M tokens"]


def test_extract_tables_empty():
    """Verify empty or table-free HTML returns an empty list without error."""
    assert DataExtractor.extract_tables("<html><body><p>No table here</p></body></html>") == []
    assert DataExtractor.extract_tables("") == []


def test_extract_links_with_base_url_resolution():
    """Verify relative URLs are correctly resolved using base_url and invalid links filtered."""
    base_url = "https://ai-research.org/catalog/index.html"
    links = DataExtractor.extract_links(SAMPLE_HTML_WITH_TABLE_AND_LINKS, base_url=base_url)

    # Filtered: javascript link ignored, empty link ignored
    urls = [link["url"] for link in links]
    texts = [link["text"] for link in links]

    assert "https://ai-research.org/docs/guide.html" in urls
    assert "https://example.com/external-paper" in urls
    assert "https://ai-research.org/api/v1/endpoints" in urls
    assert "Documentation Guide" in texts
    assert "External Research Paper" in texts
    assert "Invalid Script Link" not in texts


def test_extract_links_without_base_url():
    """Verify relative URLs are preserved as-is when base_url is not specified."""
    links = DataExtractor.extract_links(SAMPLE_HTML_WITH_TABLE_AND_LINKS)
    hrefs = [link["url"] for link in links]
    assert "/docs/guide.html" in hrefs
    assert "https://example.com/external-paper" in hrefs


def test_extract_structured_content():
    """Verify aggregated extraction of tables, links, and headings."""
    base_url = "https://ai-research.org"
    structured = DataExtractor.extract_structured_content(SAMPLE_HTML_WITH_TABLE_AND_LINKS, base_url=base_url)

    assert "tables" in structured
    assert "links" in structured
    assert "headings" in structured

    assert len(structured["tables"]) == 1
    assert len(structured["links"]) >= 3
    headings = structured["headings"]
    assert any(h["level"] == "h1" and "Top AI Models 2026" in h["text"] for h in headings)
    assert any(h["level"] == "h2" and "Benchmark Overview" in h["text"] for h in headings)
