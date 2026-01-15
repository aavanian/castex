"""Fetch episode description from BBC programme pages."""

from bs4 import BeautifulSoup


def parse_bbc_html(html: str) -> str | None:
    """Extract episode description from BBC page HTML.

    Returns the description text or None if not found.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Try meta description first (most reliable)
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        content = meta.get("content")
        if content and isinstance(content, str):
            return content

    # Try og:description as fallback
    og_meta = soup.find("meta", attrs={"property": "og:description"})
    if og_meta:
        content = og_meta.get("content")
        if content and isinstance(content, str):
            return content

    return None
