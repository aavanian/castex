#!/usr/bin/env python3
"""Fetch RSS feed and save to JSON.

Usage:
    uv run python scripts/update_feed.py

This script fetches the current RSS feed from all configured podcasts
and saves the feed items as JSON files. Historic feed data is loaded
and merged if it exists.
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

from castex.config import Settings
from castex.feed import merge_feed_items
from castex.models import FeedItem
from castex.podcasts.registry import get_feed_provider, list_podcasts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _feed_item_to_dict(item: FeedItem) -> dict[str, Any]:
    """Convert a FeedItem to a dictionary for JSON serialization."""
    return {
        "guid": item.guid,
        "title": item.title,
        "published": item.published.isoformat(),
        "link": item.link,
        "description": item.description,
    }


def _dict_to_feed_item(data: dict[str, Any]) -> FeedItem:
    """Convert a dictionary from JSON to a FeedItem."""
    return FeedItem(
        guid=data["guid"],
        title=data["title"],
        published=date.fromisoformat(data["published"]),
        link=data["link"],
        description=data.get("description"),
    )


def save_feed_items(items: list[FeedItem], path: Path) -> None:
    """Save feed items to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump([_feed_item_to_dict(item) for item in items], f, indent=2)


def load_feed_items(path: Path) -> list[FeedItem]:
    """Load feed items from a JSON file. Returns empty list if file doesn't exist."""
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [_dict_to_feed_item(item) for item in data]


def main() -> None:
    """Main function to fetch and save feed data."""
    settings = Settings()

    for podcast_id in list_podcasts():
        logger.info("Processing podcast: %s", podcast_id)

        provider = get_feed_provider(podcast_id)
        if provider is None:
            logger.warning("No feed provider found for %s", podcast_id)
            continue

        logger.info("Fetching current RSS feed...")
        try:
            current_items = provider.fetch_current_feed()
            logger.info("Fetched %d items from RSS feed", len(current_items))
        except Exception as e:
            logger.error("Failed to fetch RSS feed: %s", e)
            continue

        historic_path = settings.historic_feed_json_path(podcast_id)
        historic_items = load_feed_items(historic_path)
        if historic_items:
            logger.info("Loaded %d items from historic feed", len(historic_items))

        if not provider.is_feed_complete():
            historic_items = provider.fetch_historic_feed()
            if historic_items:
                logger.info("Fetched %d historic items", len(historic_items))
                save_feed_items(historic_items, historic_path)

        merged = merge_feed_items(current_items, historic_items)
        logger.info("Merged to %d total items", len(merged))

        feed_path = settings.feed_json_path(podcast_id)
        save_feed_items(merged, feed_path)
        logger.info("Saved feed to %s", feed_path)


if __name__ == "__main__":
    main()
