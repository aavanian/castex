"""Tests for search module."""

from datetime import date

from castex.models import Episode
from castex.search import SearchIndex


def test_search_by_title() -> None:
    """Test searching episodes by title."""
    episodes = [
        Episode(
            id="siege-malta",
            title="The Siege of Malta",
            broadcast_date=date(2020, 1, 1),
            contributors=["Prof. A"],
            description="Ottoman siege",
            source_url="https://example.com/1",
            categories=["History", "Medieval"],
            braggoscope_url=None,
        ),
        Episode(
            id="plato-republic",
            title="Plato's Republic",
            broadcast_date=date(2020, 2, 1),
            contributors=["Dr. B"],
            description="Ancient philosophy",
            source_url="https://example.com/2",
            categories=["Philosophy", "Ancient"],
            braggoscope_url=None,
        ),
    ]

    index = SearchIndex(episodes)
    results = index.search("Malta")

    assert len(results) == 1
    assert results[0].id == "siege-malta"


def test_search_by_description() -> None:
    """Test searching episodes by description."""
    episodes = [
        Episode(
            id="ep1",
            title="Episode One",
            broadcast_date=date(2020, 1, 1),
            contributors=[],
            description="Discussion about quantum physics",
            source_url="https://example.com/1",
            categories=["Science"],
            braggoscope_url=None,
        ),
    ]

    index = SearchIndex(episodes)
    results = index.search("quantum")

    assert len(results) == 1
    assert results[0].id == "ep1"


def test_search_by_category() -> None:
    """Test searching episodes by category."""
    episodes = [
        Episode(
            id="ep1",
            title="Episode One",
            broadcast_date=date(2020, 1, 1),
            contributors=[],
            description="Test",
            source_url="https://example.com/1",
            categories=["Philosophy", "Ancient", "Greece"],
            braggoscope_url=None,
        ),
    ]

    index = SearchIndex(episodes)
    results = index.search("Philosophy")

    assert len(results) == 1


def test_search_multiple_terms_or() -> None:
    """Test that multiple search terms are ORed together."""
    episodes = [
        Episode(
            id="ep1",
            title="Malta History",
            broadcast_date=date(2020, 1, 1),
            contributors=[],
            description="",
            source_url="https://example.com/1",
            categories=[],
            braggoscope_url=None,
        ),
        Episode(
            id="ep2",
            title="Greece Philosophy",
            broadcast_date=date(2020, 2, 1),
            contributors=[],
            description="",
            source_url="https://example.com/2",
            categories=[],
            braggoscope_url=None,
        ),
    ]

    index = SearchIndex(episodes)
    results = index.search("Malta Greece")

    assert len(results) == 2


def test_search_empty_query() -> None:
    """Test that empty query returns empty results."""
    episodes = [
        Episode(
            id="ep1",
            title="Test",
            broadcast_date=date(2020, 1, 1),
            contributors=[],
            description="",
            source_url="https://example.com/1",
            categories=[],
            braggoscope_url=None,
        ),
    ]

    index = SearchIndex(episodes)
    results = index.search("")

    assert results == []


def test_search_no_results() -> None:
    """Test search with no matching results."""
    episodes = [
        Episode(
            id="ep1",
            title="Malta",
            broadcast_date=date(2020, 1, 1),
            contributors=[],
            description="",
            source_url="https://example.com/1",
            categories=[],
            braggoscope_url=None,
        ),
    ]

    index = SearchIndex(episodes)
    results = index.search("nonexistent")

    assert results == []
