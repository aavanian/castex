"""Episode data model and type definitions."""

import re
from dataclasses import dataclass
from datetime import date


def make_episode_id(title: str) -> str:
    """Create a URL-friendly slug from an episode title."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


def make_braggoscope_url(slug: str, broadcast_date: date) -> str:
    """Create a braggoscope URL from slug and broadcast date.

    Format: https://www.braggoscope.com/YYYY/MM/DD/{slug}.html
    """
    return f"https://www.braggoscope.com/{broadcast_date:%Y/%m/%d}/{slug}.html"


@dataclass
class Episode:
    """Represents a single In Our Time episode."""

    id: str
    title: str
    broadcast_date: date
    contributors: list[str]
    description: str | None
    source_url: str
    categories: list[str]
    braggoscope_url: str | None
