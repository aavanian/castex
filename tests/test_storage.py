"""Tests for storage module."""

from datetime import date
from pathlib import Path

from castex.models import Episode
from castex.storage import load_episodes, save_episodes


def test_save_and_load_episodes(tmp_path: Path) -> None:
    """Test saving and loading episodes to/from JSON."""
    episodes = [
        Episode(
            id="episode-one",
            title="Episode One",
            broadcast_date=date(2020, 1, 15),
            contributors=["Dr. A (Oxford)"],
            description="Description one.",
            source_url="https://example.com/ep1",
            categories=["History", "Britain"],
            braggoscope_url=None,
        ),
        Episode(
            id="episode-two",
            title="Episode Two",
            broadcast_date=date(2020, 2, 20),
            contributors=["Prof. B (Cambridge)", "Dr. C (Edinburgh)"],
            description=None,
            source_url="https://example.com/ep2",
            categories=["Philosophy", "Ancient"],
            braggoscope_url="https://braggoscope.com/ep2",
        ),
    ]

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    save_episodes(episodes, data_dir)
    loaded = load_episodes(data_dir)

    assert len(loaded) == 2
    assert loaded[0].id == "episode-one"
    assert loaded[0].broadcast_date == date(2020, 1, 15)
    assert loaded[1].contributors == ["Prof. B (Cambridge)", "Dr. C (Edinburgh)"]
    assert loaded[1].description is None


def test_load_episodes_empty_directory(tmp_path: Path) -> None:
    """Test loading from a directory with no episodes file returns empty list."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    loaded = load_episodes(data_dir)

    assert loaded == []
