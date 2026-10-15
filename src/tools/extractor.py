"""Utility tools for structured data extraction and search."""

from typing import Any, Dict, List
from bs4 import BeautifulSoup


class DataExtractor:
    """Extracts structured tables, articles, and key-value pairs from HTML."""

    @staticmethod
    def extract_links(html: str, base_url: str = "") -> List[Dict[str, str]]:
        """Extract all hyperlink tags with text and href attributes."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            if text and len(text) > 2:
                href = a["href"]
                links.append({"text": text, "url": href})
        return links

    @staticmethod
    def extract_tables(html: str) -> List[List[List[str]]]:
        """Parse HTML tables into structured 2D lists of cells."""
        soup = BeautifulSoup(html, "html.parser")
        tables = []
        for table in soup.find_all("table"):
            table_data = []
            for row in table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                if cells:
                    table_data.append(cells)
            if table_data:
                tables.append(table_data)
        return tables
