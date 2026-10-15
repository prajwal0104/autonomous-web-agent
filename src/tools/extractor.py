import urllib.parse
from typing import Any, Dict, List
from bs4 import BeautifulSoup


class DataExtractor:
    """Extracts structured tables, links, and text from HTML documents."""

    @staticmethod
    def extract_links(html: str, base_url: str = "") -> List[Dict[str, str]]:
        """Extract all hyperlink tags with text and href attributes, resolving relative paths."""
        soup = BeautifulSoup(html, "html.parser")
        links: List[Dict[str, str]] = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"].strip()
            if not text or len(text) < 2 or href.startswith("javascript:") or href.startswith("mailto:"):
                continue
            if base_url and not href.startswith(("http://", "https://")):
                resolved_url = urllib.parse.urljoin(base_url, href)
            else:
                resolved_url = href
            links.append({"text": text, "url": resolved_url})
        return links

    @staticmethod
    def extract_tables(html: str) -> List[List[List[str]]]:
        """Parse HTML tables into structured 2D lists of cells."""
        soup = BeautifulSoup(html, "html.parser")
        tables: List[List[List[str]]] = []
        for table in soup.find_all("table"):
            table_data: List[List[str]] = []
            for row in table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                if cells:
                    table_data.append(cells)
            if table_data:
                tables.append(table_data)
        return tables

    @staticmethod
    def extract_structured_content(html: str, base_url: str = "") -> Dict[str, Any]:
        """Aggregate tables, links, and headings from an HTML document."""
        soup = BeautifulSoup(html, "html.parser")
        headings = [
            {"level": h.name, "text": h.get_text(strip=True)}
            for h in soup.find_all(["h1", "h2", "h3"])
            if h.get_text(strip=True)
        ]
        return {
            "tables": DataExtractor.extract_tables(html),
            "links": DataExtractor.extract_links(html, base_url=base_url),
            "headings": headings,
        }
