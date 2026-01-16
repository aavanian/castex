"""Tests for SQLite database module."""

from datetime import date
from pathlib import Path

from castex.db import Database
from castex.models import Episode


def test_database_create_tables(tmp_path: Path) -> None:
    """Test that database creates tables on initialization."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)

    assert db_path.exists()
    db.close()


def test_database_upsert_and_get_episode(tmp_path: Path) -> None:
    """Test inserting and retrieving an episode."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)

    episode = Episode(
        id="siege-malta",
        podcast_id="in_our_time",
        title="The Siege of Malta",
        broadcast_date=date(2020, 1, 15),
        contributors=["Prof. A", "Dr. B"],
        description="A discussion about Malta.",
        source_url="https://example.com/ep1",
        categories=["History", "Medieval"],
        braggoscope_url="https://braggoscope.com/ep1",
        reading_list=["Book 1", "Book 2"],
    )

    db.upsert_episode(episode)
    retrieved = db.get_episode("siege-malta")

    assert retrieved is not None
    assert retrieved.id == "siege-malta"
    assert retrieved.podcast_id == "in_our_time"
    assert retrieved.title == "The Siege of Malta"
    assert retrieved.broadcast_date == date(2020, 1, 15)
    assert retrieved.contributors == ["Prof. A", "Dr. B"]
    assert retrieved.description == "A discussion about Malta."
    assert retrieved.categories == ["History", "Medieval"]
    assert retrieved.reading_list == ["Book 1", "Book 2"]
    db.close()


def test_database_get_all_episodes(tmp_path: Path) -> None:
    """Test retrieving all episodes."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)

    episodes = [
        Episode(
            id="ep1",
            podcast_id="in_our_time",
            title="Episode One",
            broadcast_date=date(2020, 1, 1),
            contributors=[],
            description=None,
            source_url="https://example.com/ep1",
            categories=[],
            braggoscope_url=None,
        ),
        Episode(
            id="ep2",
            podcast_id="in_our_time",
            title="Episode Two",
            broadcast_date=date(2020, 2, 1),
            contributors=[],
            description=None,
            source_url="https://example.com/ep2",
            categories=[],
            braggoscope_url=None,
        ),
    ]

    for ep in episodes:
        db.upsert_episode(ep)

    all_episodes = db.get_all_episodes()

    assert len(all_episodes) == 2
    db.close()


def test_database_upsert_updates_existing(tmp_path: Path) -> None:
    """Test that upsert updates an existing episode."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)

    original = Episode(
        id="ep1",
        podcast_id="in_our_time",
        title="Episode One",
        broadcast_date=date(2020, 1, 1),
        contributors=[],
        description="Original description",
        source_url="https://example.com/ep1",
        categories=[],
        braggoscope_url=None,
    )

    db.upsert_episode(original)

    updated = Episode(
        id="ep1",
        podcast_id="in_our_time",
        title="Episode One",
        broadcast_date=date(2020, 1, 1),
        contributors=["Prof. A"],
        description="Updated description",
        source_url="https://example.com/ep1",
        categories=["History"],
        braggoscope_url=None,
    )

    db.upsert_episode(updated)

    retrieved = db.get_episode("ep1")

    assert retrieved is not None
    assert retrieved.description == "Updated description"
    assert retrieved.contributors == ["Prof. A"]
    assert retrieved.categories == ["History"]
    db.close()


def test_database_get_episode_not_found(tmp_path: Path) -> None:
    """Test that get_episode returns None for non-existent episode."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)

    result = db.get_episode("nonexistent")

    assert result is None
    db.close()


def test_database_search(tmp_path: Path) -> None:
    """Test full-text search functionality."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)

    episodes = [
        Episode(
            id="siege-malta",
            podcast_id="in_our_time",
            title="The Siege of Malta",
            broadcast_date=date(2020, 1, 1),
            contributors=["Prof. A"],
            description="Ottoman siege",
            source_url="https://example.com/ep1",
            categories=["History", "Medieval"],
            braggoscope_url=None,
        ),
        Episode(
            id="plato-republic",
            podcast_id="in_our_time",
            title="Plato's Republic",
            broadcast_date=date(2020, 2, 1),
            contributors=["Dr. B"],
            description="Ancient philosophy",
            source_url="https://example.com/ep2",
            categories=["Philosophy", "Ancient"],
            braggoscope_url=None,
        ),
    ]

    for ep in episodes:
        db.upsert_episode(ep)

    results = db.search("Malta")

    assert len(results) == 1
    assert results[0].id == "siege-malta"
    db.close()


def test_database_search_empty_query(tmp_path: Path) -> None:
    """Test that empty query returns empty list."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)

    results = db.search("")

    assert results == []
    db.close()


def test_database_filter_by_podcast(tmp_path: Path) -> None:
    """Test filtering episodes by podcast_id."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)

    episodes = [
        Episode(
            id="ep1",
            podcast_id="in_our_time",
            title="IOT Episode",
            broadcast_date=date(2020, 1, 1),
            contributors=[],
            description=None,
            source_url="https://example.com/ep1",
            categories=[],
            braggoscope_url=None,
        ),
        Episode(
            id="ep2",
            podcast_id="other_podcast",
            title="Other Episode",
            broadcast_date=date(2020, 2, 1),
            contributors=[],
            description=None,
            source_url="https://example.com/ep2",
            categories=[],
            braggoscope_url=None,
        ),
    ]

    for ep in episodes:
        db.upsert_episode(ep)

    iot_episodes = db.get_episodes_by_podcast("in_our_time")

    assert len(iot_episodes) == 1
    assert iot_episodes[0].id == "ep1"
    db.close()
