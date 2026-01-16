#!/usr/bin/env python3
"""Process feed items and update SQLite database.

Usage:
    uv run python scripts/update_db.py

This script reads feed items from JSON, enriches them with data from
BBC pages, classifies them with LLM, and saves to SQLite database.
"""

import asyncio
import logging
import time
from datetime import date
from pathlib import Path
from typing import Any

from castex.classifier import classify_episode
from castex.config import Settings
from castex.db import Database
from castex.models import Episode, FeedItem, make_braggoscope_url, make_episode_id
from castex.podcasts.registry import get_enricher, list_podcasts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

REQUEST_DELAY = 1.0


def load_feed_items_json(path: Path) -> list[dict[str, Any]]:
    """Load feed items from JSON file."""
    import json

    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data: list[dict[str, Any]] = json.load(f)
        return data


def dict_to_feed_item(data: dict[str, Any]) -> FeedItem:
    """Convert a dictionary from JSON to a FeedItem."""
    return FeedItem(
        guid=data["guid"],
        title=data["title"],
        published=date.fromisoformat(data["published"]),
        link=data["link"],
        description=data.get("description"),
    )


async def process_episode(
    item: FeedItem,
    podcast_id: str,
    settings: Settings,
) -> Episode:
    """Process a single feed item into an Episode."""
    logger.info("Processing: %s", item.title)

    enriched: dict[str, Any] = {
        "description": item.description,
        "contributors": [],
        "reading_list": [],
    }
    enricher = get_enricher(podcast_id)
    if enricher:
        try:
            enriched = await enricher.enrich(item)
        except Exception as e:
            logger.warning("Failed to enrich %s: %s", item.title, e)

    description = enriched.get("description") or item.description
    contributors = enriched.get("contributors", [])
    reading_list = enriched.get("reading_list", [])

    categories = await classify_episode(
        title=item.title,
        description=description,
        contributors=contributors,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
    )

    episode_id = make_episode_id(item.title)
    braggoscope_url = make_braggoscope_url(episode_id, item.published)

    return Episode(
        id=episode_id,
        podcast_id=podcast_id,
        title=item.title,
        broadcast_date=item.published,
        contributors=contributors,
        description=description,
        source_url=item.link,
        categories=categories,
        braggoscope_url=braggoscope_url,
        reading_list=reading_list,
    )


async def main() -> None:
    """Main function to process feed and update database."""
    settings = Settings()

    db = Database(settings.db_path)
    existing_ids = {ep.id for ep in db.get_all_episodes()}
    logger.info("Found %d existing episodes in database", len(existing_ids))

    total_new_count = 0

    for podcast_id in list_podcasts():
        logger.info("Processing podcast: %s", podcast_id)

        feed_path = settings.feed_json_path(podcast_id)
        feed_data = load_feed_items_json(feed_path)
        if not feed_data:
            logger.info("No feed data found at %s", feed_path)
            continue

        logger.info("Loaded %d feed items", len(feed_data))

        new_count = 0
        for item_data in feed_data:
            item = dict_to_feed_item(item_data)
            episode_id = make_episode_id(item.title)

            if episode_id in existing_ids:
                continue

            episode = await process_episode(item, podcast_id, settings)
            db.upsert_episode(episode)
            new_count += 1
            existing_ids.add(episode_id)

            time.sleep(REQUEST_DELAY)

        logger.info("Added %d new episodes for %s", new_count, podcast_id)
        total_new_count += new_count

    db.close()
    logger.info("Added %d total new episodes to database", total_new_count)


if __name__ == "__main__":
    asyncio.run(main())
