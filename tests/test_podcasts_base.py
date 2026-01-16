"""Tests for podcast provider protocols."""

from datetime import date
from typing import Any

from castex.models import FeedItem
from castex.podcasts.base import EpisodeEnricher, FeedProvider


class MockFeedProvider:
    """Mock implementation of FeedProvider for testing protocol compliance."""

    def fetch_current_feed(self) -> list[FeedItem]:
        """Return a mock feed."""
        return [
            FeedItem(
                guid="test-guid-1",
                title="Test Episode",
                published=date(2020, 1, 1),
                link="https://example.com/ep1",
                description="Test description",
            )
        ]

    def fetch_historic_feed(self) -> list[FeedItem]:
        """Return empty historic feed."""
        return []

    def is_feed_complete(self) -> bool:
        """Indicate feed is complete."""
        return True


class MockEpisodeEnricher:
    """Mock implementation of EpisodeEnricher for testing protocol compliance."""

    async def enrich(self, item: FeedItem) -> dict[str, Any]:
        """Return enriched data."""
        return {
            "description": "Enriched description",
            "contributors": ["Prof. A"],
            "reading_list": [],
        }


def test_feed_provider_protocol_compliance() -> None:
    """Test that a class implementing FeedProvider is accepted by the protocol."""
    provider: FeedProvider = MockFeedProvider()

    items = provider.fetch_current_feed()

    assert len(items) == 1
    assert items[0].guid == "test-guid-1"
    assert items[0].title == "Test Episode"


def test_feed_provider_is_feed_complete() -> None:
    """Test is_feed_complete method."""
    provider: FeedProvider = MockFeedProvider()

    assert provider.is_feed_complete() is True


async def test_episode_enricher_protocol_compliance() -> None:
    """Test that a class implementing EpisodeEnricher is accepted by the protocol."""
    enricher: EpisodeEnricher = MockEpisodeEnricher()
    item = FeedItem(
        guid="test-guid",
        title="Test Episode",
        published=date(2020, 1, 1),
        link="https://example.com/ep",
        description="Short desc",
    )

    enriched = await enricher.enrich(item)

    assert enriched["description"] == "Enriched description"
    assert enriched["contributors"] == ["Prof. A"]
