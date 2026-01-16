"""Protocol definitions for podcast providers and enrichers."""

from typing import Any, Protocol

from castex.models import FeedItem


class FeedProvider(Protocol):
    """Provides feed items for a podcast."""

    def fetch_current_feed(self) -> list[FeedItem]:
        """Fetch and parse the current RSS feed."""
        ...

    def fetch_historic_feed(self) -> list[FeedItem]:
        """One-time scrape for historic episodes not in RSS."""
        ...

    def is_feed_complete(self) -> bool:
        """Check if RSS feed contains full history."""
        ...


class EpisodeEnricher(Protocol):
    """Enriches feed items with additional metadata."""

    async def enrich(self, item: FeedItem) -> dict[str, Any]:
        """Fetch additional data for an episode."""
        ...
