"""Tests for In Our Time episode enricher."""

from datetime import date
from typing import Any

import pytest

from castex.models import FeedItem
from castex.podcasts.in_our_time.enricher import InOurTimeEnricher


@pytest.fixture
def sample_item() -> FeedItem:
    """Create a sample feed item for testing."""
    return FeedItem(
        guid="urn:bbc:podcast:b09xyz123",
        title="The Siege of Malta (1565)",
        published=date(2017, 9, 21),
        link="https://www.bbc.co.uk/programmes/b09xyz123",
        description="Short RSS description.",
    )


async def test_enricher_calls_parser(sample_item: FeedItem, httpx_mock: Any) -> None:
    """Test that enricher fetches page and parses it."""
    html = """
    <html>
    <head>
      <meta name="description" content="Short meta description">
    </head>
    <body>
      <div class="synopsis-toggle__long">
        <p>Full description of the episode.</p>
        <p>With</p>
        <p>Professor Alice Smith</p>
        <p>and</p>
        <p>Dr. Bob Jones</p>
        <p>Reading list:</p>
        <p>Some Book by Author (Publisher, 2020)</p>
      </div>
    </body>
    </html>
    """

    httpx_mock.add_response(
        url="https://www.bbc.co.uk/programmes/b09xyz123",
        html=html,
    )

    enricher = InOurTimeEnricher()
    result = await enricher.enrich(sample_item)

    assert result["description"] == "Full description of the episode."
    assert result["contributors"] == ["Professor Alice Smith", "Dr. Bob Jones"]
    assert result["reading_list"] == ["Some Book by Author (Publisher, 2020)"]


async def test_enricher_handles_http_error(sample_item: FeedItem, httpx_mock: Any) -> None:
    """Test that enricher handles HTTP errors gracefully."""
    httpx_mock.add_response(
        url="https://www.bbc.co.uk/programmes/b09xyz123",
        status_code=404,
    )

    enricher = InOurTimeEnricher()
    result = await enricher.enrich(sample_item)

    assert result["description"] is None
    assert result["contributors"] == []
    assert result["reading_list"] == []
