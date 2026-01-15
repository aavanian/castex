#!/usr/bin/env python3
"""Update script for scraping and classifying new episodes.

Usage:
    uv run python scripts/update.py
"""

import asyncio
import logging
import time

import httpx

from castex.classifier import classify_episode
from castex.config import Settings
from castex.models import Episode, make_episode_id
from castex.scraper.bbc import parse_bbc_html
from castex.scraper.wikipedia import parse_wikipedia_html
from castex.storage import load_episodes, save_episodes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_In_Our_Time_programmes"
REQUEST_DELAY = 1.0  # Seconds between BBC page requests


async def fetch_wikipedia(client: httpx.AsyncClient) -> str:
    """Fetch the Wikipedia episode list page."""
    logger.info("Fetching Wikipedia page...")
    response = await client.get(WIKIPEDIA_URL)
    response.raise_for_status()
    return response.text


async def fetch_bbc_description(client: httpx.AsyncClient, url: str) -> str | None:
    """Fetch episode description from BBC page."""
    try:
        response = await client.get(url)
        response.raise_for_status()
        return parse_bbc_html(response.text)
    except httpx.HTTPError as e:
        logger.warning("Failed to fetch BBC page %s: %s", url, e)
        return None


async def process_new_episode(
    client: httpx.AsyncClient,
    episode_data: dict[str, object],
    settings: Settings,
) -> Episode:
    """Process a new episode: fetch description and classify."""
    title = str(episode_data["title"])
    source_url = str(episode_data["source_url"])
    logger.info("Processing: %s", title)

    # Fetch description from BBC
    description = await fetch_bbc_description(client, source_url)

    # Classify with LLM
    contributors = episode_data.get("contributors", [])
    if not isinstance(contributors, list):
        contributors = []
    contributors = [str(c) for c in contributors]

    categories = await classify_episode(
        title=title,
        description=description,
        contributors=contributors,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
    )

    # Generate braggoscope URL
    episode_id = make_episode_id(title)
    braggoscope_url = f"https://www.braggoscope.com/episode/{episode_id}"

    from datetime import date

    broadcast_date = episode_data.get("broadcast_date")
    if not isinstance(broadcast_date, date):
        broadcast_date = date.today()

    return Episode(
        id=episode_id,
        title=title,
        broadcast_date=broadcast_date,
        contributors=contributors,
        description=description,
        source_url=source_url,
        categories=categories,
        braggoscope_url=braggoscope_url,
    )


async def main() -> None:
    """Main update function."""
    settings = Settings()

    # Load existing episodes
    existing_episodes = load_episodes(settings.data_dir)
    existing_ids = {ep.id for ep in existing_episodes}
    logger.info("Loaded %d existing episodes", len(existing_episodes))

    async with httpx.AsyncClient(
        headers={"User-Agent": "CastexBot/1.0 (podcast-archive)"},
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        # Fetch and parse Wikipedia
        html = await fetch_wikipedia(client)
        scraped_episodes = parse_wikipedia_html(html)
        logger.info("Found %d episodes on Wikipedia", len(scraped_episodes))

        # Find new episodes
        new_episode_data = []
        for ep_data in scraped_episodes:
            episode_id = make_episode_id(str(ep_data["title"]))
            if episode_id not in existing_ids:
                new_episode_data.append(ep_data)

        logger.info("Found %d new episodes to process", len(new_episode_data))

        if not new_episode_data:
            logger.info("No new episodes to process")
            return

        # Process new episodes
        new_episodes = []
        for ep_data in new_episode_data:
            episode = await process_new_episode(client, ep_data, settings)
            new_episodes.append(episode)
            time.sleep(REQUEST_DELAY)  # Rate limiting

        # Merge and save
        all_episodes = existing_episodes + new_episodes
        all_episodes.sort(key=lambda ep: ep.broadcast_date, reverse=True)

        settings.data_dir.mkdir(parents=True, exist_ok=True)
        save_episodes(all_episodes, settings.data_dir)
        logger.info("Saved %d total episodes", len(all_episodes))


if __name__ == "__main__":
    asyncio.run(main())
