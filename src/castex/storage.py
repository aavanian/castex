"""Read/write episode data to JSON files."""

import json
from datetime import date
from pathlib import Path
from typing import Any

from castex.models import Episode

EPISODES_FILENAME = "episodes.json"


def save_episodes(episodes: list[Episode], data_dir: Path) -> None:
    """Save episodes to a JSON file."""
    data = [_episode_to_dict(ep) for ep in episodes]
    filepath = data_dir / EPISODES_FILENAME
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_episodes(data_dir: Path) -> list[Episode]:
    """Load episodes from a JSON file. Returns empty list if file doesn't exist."""
    filepath = data_dir / EPISODES_FILENAME
    if not filepath.exists():
        return []
    with filepath.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [_dict_to_episode(d) for d in data]


def _episode_to_dict(episode: Episode) -> dict[str, Any]:
    """Convert an Episode to a dictionary for JSON serialization."""
    return {
        "id": episode.id,
        "title": episode.title,
        "broadcast_date": episode.broadcast_date.isoformat(),
        "contributors": episode.contributors,
        "description": episode.description,
        "source_url": episode.source_url,
        "categories": episode.categories,
        "braggoscope_url": episode.braggoscope_url,
        "reading_list": episode.reading_list,
    }


def _dict_to_episode(data: dict[str, Any]) -> Episode:
    """Convert a dictionary from JSON to an Episode."""
    return Episode(
        id=data["id"],
        title=data["title"],
        broadcast_date=date.fromisoformat(data["broadcast_date"]),
        contributors=data["contributors"],
        description=data["description"],
        source_url=data["source_url"],
        categories=data["categories"],
        braggoscope_url=data["braggoscope_url"],
        reading_list=data.get("reading_list", []),
    )
