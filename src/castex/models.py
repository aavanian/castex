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
