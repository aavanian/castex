"""Parse episode list from Wikipedia.

DEPRECATED: This module is deprecated in favor of the RSS-first architecture.
The BBC RSS feed contains the complete episode history, making Wikipedia
scraping unnecessary. This module is kept for backward compatibility but
will be removed in a future version.

Use castex.podcasts.in_our_time.feed.InOurTimeFeedProvider instead.
"""

import re
from datetime import date
from typing import Any

from bs4 import BeautifulSoup


def parse_wikipedia_html(html: str) -> list[dict[str, Any]]:
    """Parse episode data from Wikipedia HTML.

    Returns a list of dictionaries with episode data (not full Episode objects,
    since description and categories are fetched/generated separately).
    """
    soup = BeautifulSoup(html, "html.parser")
    episodes: list[dict[str, Any]] = []

    for table in soup.find_all("table", class_="wikitable"):
        rows = table.find_all("tr")
        for row in rows[1:]:  # Skip header row
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            episode_data = _parse_row(cells)
            if episode_data:
                episodes.append(episode_data)

    return episodes


def _parse_row(cells: list[Any]) -> dict[str, Any] | None:
    """Parse a single table row into episode data."""
    date_cell = cells[0]
    title_cell = cells[1]
    contributors_cell = cells[2]

    # Extract BBC URL and date from first cell
    link = date_cell.find("a")
    if not link:
        return None

    source_url = link.get("href", "")
    date_text = link.get_text(strip=True)
    broadcast_date = _parse_date(date_text)
    if not broadcast_date:
        return None

    # Extract title (strip Wikipedia internal links, keep text)
    title = " ".join(title_cell.get_text(separator=" ", strip=True).split())

    # Extract contributors
    contributors = _parse_contributors(contributors_cell)

    return {
        "title": title,
        "broadcast_date": broadcast_date,
        "source_url": source_url,
        "contributors": contributors,
    }


def _parse_date(text: str) -> date | None:
    """Parse date from text like '15 October 1998'."""
    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }

    match = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", text)
    if not match:
        return None

    day = int(match.group(1))
    month_name = match.group(2).lower()
    year = int(match.group(3))

    month = months.get(month_name)
    if not month:
        return None

    return date(year, month, day)


def _normalize_text(text: str) -> str:
    """Normalize whitespace and fix spacing around punctuation."""
    # Collapse multiple spaces to single space
    text = re.sub(r"\s+", " ", text)
    # Remove space before punctuation (comma, period, semicolon, colon, apostrophe)
    text = re.sub(r"\s+([,\.;:'])", r"\1", text)
    return text.strip()


def _parse_contributors(cell: Any) -> list[str]:
    """Parse contributors from the cell."""
    contributors: list[str] = []

    # Look for list items
    for li in cell.find_all("li"):
        text = li.get_text(separator=" ", strip=True)
        text = _normalize_text(text)
        if text:
            contributors.append(text)

    # If no list items, get the cell text directly
    if not contributors:
        text = cell.get_text(separator=" ", strip=True)
        text = _normalize_text(text)
        if text:
            contributors.append(text)

    return contributors
