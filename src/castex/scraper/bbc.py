"""Fetch episode description from BBC programme pages."""

import re
from typing import TypedDict

from bs4 import BeautifulSoup, Tag

# Patterns to identify paragraphs we should stop parsing at
_SKIP_PATTERNS = [
    r"^This episode was first broadcast",
    r"^Spanning history, religion",
    r"^In Our Time is a BBC",
    r"^In Our Time from BBC",
]


class BBCEpisodeData(TypedDict, total=False):
    """Parsed data from a BBC episode page."""

    description: str | None
    short_description: str | None
    contributors: list[str]
    reading_list: list[str]


def parse_bbc_html(html: str) -> BBCEpisodeData:
    """Extract episode data from BBC page HTML.

    Returns a dict with description, contributors, and reading list.
    """
    soup = BeautifulSoup(html, "html.parser")
    result: BBCEpisodeData = {}

    # Get short description from meta tags
    result["short_description"] = _get_meta_description(soup)

    # Parse the long synopsis - handles both old and new formats
    long_synopsis = soup.find("div", class_="synopsis-toggle__long")
    if long_synopsis and isinstance(long_synopsis, Tag):
        parsed = _parse_long_synopsis(long_synopsis)
        result["description"] = parsed["description"]
        result["contributors"] = parsed["contributors"]
        result["reading_list"] = parsed["reading_list"]
    else:
        # Fall back to short synopsis for description only
        result["description"] = _get_short_description(soup)
        result["contributors"] = []
        result["reading_list"] = []

    return result


def parse_rss_description_html(html: str) -> BBCEpisodeData:
    """Parse episode data from RSS feed description HTML.

    The RSS description contains HTML with <p> tags in the same format
    as the BBC page synopsis, so we can reuse the parsing logic.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Get all <p> tags directly (RSS description is just <p> tags, no wrapper div)
    paragraphs = soup.find_all("p")
    if not paragraphs:
        # No <p> tags, treat as plain text
        text = soup.get_text(strip=True)
        return {"description": text, "contributors": [], "reading_list": []}

    p_texts = [p.get_text(separator=" ", strip=True) for p in paragraphs]

    # Detect format and parse (reuse existing logic)
    if len(p_texts) > 1 and p_texts[1].strip().lower() == "with":
        return _parse_new_format(p_texts)
    else:
        return _parse_old_format(p_texts)


def _get_meta_description(soup: BeautifulSoup) -> str | None:
    """Get description from meta tags."""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        content = meta.get("content")
        if content and isinstance(content, str):
            return content

    og_meta = soup.find("meta", attrs={"property": "og:description"})
    if og_meta:
        content = og_meta.get("content")
        if content and isinstance(content, str):
            return content

    return None


def _get_short_description(soup: BeautifulSoup) -> str | None:
    """Get description from short synopsis div."""
    short_synopsis = soup.find("div", class_="synopsis-toggle__short")
    if short_synopsis:
        paragraphs = short_synopsis.find_all("p")
        if paragraphs:
            text = "\n\n".join(p.get_text(separator=" ", strip=True) for p in paragraphs)
            return _clean_text(text)
    return None


def _clean_text(text: str) -> str:
    """Clean up text: normalize whitespace, fix spacing."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_skip_paragraph(text: str) -> bool:
    """Check if paragraph matches a skip pattern (boilerplate text)."""
    return any(re.match(pattern, text) for pattern in _SKIP_PATTERNS)


def _parse_long_synopsis(synopsis_div: Tag) -> BBCEpisodeData:
    """Parse the long synopsis div, handling both old and new formats.

    Old format: Single <p> with "With Name, Title; Name, Title." at end
    New format: Multiple <p> elements with structured sections
    """
    paragraphs = synopsis_div.find_all("p")
    if not paragraphs:
        return {"description": None, "contributors": [], "reading_list": []}

    # Get text content of each paragraph
    p_texts = [p.get_text(separator=" ", strip=True) for p in paragraphs]

    # Detect format: new format has a standalone "With" paragraph
    if len(p_texts) > 1 and p_texts[1].strip().lower() == "with":
        return _parse_new_format(p_texts)
    else:
        return _parse_old_format(p_texts)


def _parse_old_format(p_texts: list[str]) -> BBCEpisodeData:
    """Parse old format where everything is in one or few paragraphs.

    Contributors are embedded at end: "With Name, Title; Name, Title."
    """
    # Join all paragraphs (usually just one)
    full_text = "\n\n".join(p_texts)
    full_text = _clean_text(full_text)

    contributors: list[str] = []

    # Look for "With <name>, <title>; <name>, <title>." pattern at end
    match = re.search(
        r"\s*With\s+([A-Z][^.]+(?:;\s*[A-Z][^.]+)*)\.\s*$",
        full_text,
        re.IGNORECASE,
    )

    if match:
        description = full_text[: match.start()].strip()
        contributors_text = match.group(1)
        for contrib in contributors_text.split(";"):
            contrib = contrib.strip()
            if contrib:
                contributors.append(contrib)
    else:
        description = full_text

    return {
        "description": description or None,
        "contributors": contributors,
        "reading_list": [],
    }


def _parse_new_format(p_texts: list[str]) -> BBCEpisodeData:
    """Parse new format with structured paragraphs.

    Structure:
    - First <p>: description
    - <p>With</p>: marker
    - <p>Name<br/>Title</p>: contributors (may have <p>and</p> between)
    - <p>Producer: ...</p>: ignored
    - <p>Reading list:</p>: marker
    - <p>Book reference</p>: reading list items
    - Boilerplate paragraphs: ignored
    """
    description = _clean_text(p_texts[0]) if p_texts else None
    contributors: list[str] = []
    reading_list: list[str] = []

    # State machine for parsing
    state = "after_description"  # States: after_description, contributors, reading_list

    for text in p_texts[1:]:
        text_stripped = text.strip()
        text_lower = text_stripped.lower()

        # Skip boilerplate
        if _is_skip_paragraph(text_stripped):
            break

        # State transitions
        if text_lower == "with":
            state = "contributors"
            continue

        if text_lower == "reading list:":
            state = "reading_list"
            continue

        if text_stripped.startswith("Producer:"):
            state = "after_producer"
            continue

        # Skip "and" connectors
        if text_lower == "and":
            continue

        # Collect based on state
        if state == "contributors":
            # Contributor format: "Name<br/>Title" becomes "Name Title"
            contributors.append(text_stripped)
        elif state == "reading_list":
            reading_list.append(text_stripped)

    return {
        "description": description,
        "contributors": contributors,
        "reading_list": reading_list,
    }
