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


def test_search_substring_matching() -> None:
    """Test that partial word search finds matching episodes."""
    episodes = [
        Episode(
            id="aristotle-ethics",
            title="Aristotle's Nicomachean Ethics",
            broadcast_date=date(2020, 1, 1),
            contributors=["Prof. A"],
            description="Greek philosophy",
            source_url="https://example.com/1",
            categories=["Philosophy"],
            braggoscope_url=None,
        ),
        Episode(
            id="aristocracy",
            title="The Rise of Aristocracy",
            broadcast_date=date(2020, 2, 1),
            contributors=["Dr. B"],
            description="Social classes",
            source_url="https://example.com/2",
            categories=["History"],
            braggoscope_url=None,
        ),
        Episode(
            id="unrelated",
            title="Quantum Physics",
            broadcast_date=date(2020, 3, 1),
            contributors=[],
            description="Science topic",
            source_url="https://example.com/3",
            categories=["Science"],
            braggoscope_url=None,
        ),
    ]

    index = SearchIndex(episodes)

    # Prefix search: "aristo" should find both aristotle and aristocracy
    results = index.search("aristo")
    assert len(results) == 2
    result_ids = {r.id for r in results}
    assert result_ids == {"aristotle-ethics", "aristocracy"}

    # Infix search: "istotle" should find aristotle
    results = index.search("istotle")
    assert len(results) == 1
    assert results[0].id == "aristotle-ethics"


def test_search_by_reading_list() -> None:
    """Test searching episodes by reading list content."""
    episodes = [
        Episode(
            id="emily-dickinson",
            title="Emily Dickinson",
            broadcast_date=date(2017, 5, 4),
            contributors=["Fiona Green"],
            description="American poet",
            source_url="https://example.com/1",
            categories=["Literature"],
            braggoscope_url=None,
            reading_list=[
                "Christopher Benfey, A Summer of Hummingbirds (Penguin Books, 2009)",
            ],
        ),
        Episode(
            id="other-episode",
            title="Other Episode",
            broadcast_date=date(2020, 1, 1),
            contributors=[],
            description="Unrelated",
            source_url="https://example.com/2",
            categories=["History"],
            braggoscope_url=None,
        ),
    ]

    index = SearchIndex(episodes)
    results = index.search("Hummingbirds")

    assert len(results) == 1
    assert results[0].id == "emily-dickinson"
