#!/usr/bin/env python3
"""Migrate braggoscope URLs to the new date-based format.

Usage:
    uv run python scripts/migrate_braggoscope_urls.py
"""

import logging

from castex.config import Settings
from castex.models import make_braggoscope_url
from castex.storage import load_episodes, save_episodes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Migrate braggoscope URLs to new format."""
    settings = Settings()

    episodes = load_episodes(settings.data_dir)
    if not episodes:
        logger.info("No episodes found")
        return

    logger.info("Loaded %d episodes", len(episodes))

    updated_count = 0
    for episode in episodes:
        new_url = make_braggoscope_url(episode.id, episode.broadcast_date)
        if episode.braggoscope_url != new_url:
            logger.info("Updating %s: %s -> %s", episode.id, episode.braggoscope_url, new_url)
            episode.braggoscope_url = new_url
            updated_count += 1

    if updated_count > 0:
        save_episodes(episodes, settings.data_dir)
        logger.info("Updated %d episodes", updated_count)
    else:
        logger.info("No episodes needed updating")


if __name__ == "__main__":
    main()
