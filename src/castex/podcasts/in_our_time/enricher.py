"""In Our Time episode enricher using BBC programme pages."""

import logging
from typing import Any

import httpx

from castex.models import FeedItem
from castex.scraper.bbc import parse_bbc_html

logger = logging.getLogger(__name__)


class InOurTimeEnricher:
    """Enriches feed items with data from BBC programme pages."""

    async def enrich(self, item: FeedItem) -> dict[str, Any]:
        """Fetch and parse the BBC programme page for additional metadata."""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(item.link)
                response.raise_for_status()

            parsed = parse_bbc_html(response.text)

            return {
                "description": parsed.get("description") or parsed.get("short_description"),
                "contributors": parsed.get("contributors", []),
                "reading_list": parsed.get("reading_list", []),
            }

        except httpx.HTTPError as e:
            logger.warning("Failed to fetch BBC page %s: %s", item.link, e)
            return {
                "description": None,
                "contributors": [],
                "reading_list": [],
            }
