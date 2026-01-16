"""Tests for FastAPI server."""

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from castex.models import Episode


@pytest.fixture
def sample_episodes() -> list[Episode]:
    """Create sample episodes for testing."""
    return [
        Episode(
            id="siege-malta",
            title="The Siege of Malta",
            broadcast_date=date(2020, 1, 15),
            contributors=["Prof. A (Oxford)", "Dr. B (Cambridge)"],
            description="A discussion about the Ottoman siege.",
            source_url="https://www.bbc.co.uk/programmes/test1",
            categories=["History", "Medieval", "Mediterranean"],
            braggoscope_url="https://www.braggoscope.com/2020/01/15/siege-malta.html",
        ),
        Episode(
            id="plato-republic",
            title="Plato's Republic",
            broadcast_date=date(2020, 2, 20),
            contributors=["Prof. C"],
            description="Ancient philosophy.",
            source_url="https://www.bbc.co.uk/programmes/test2",
            categories=["Philosophy", "Ancient", "Greece"],
            braggoscope_url=None,
        ),
    ]


@pytest.fixture
def client(sample_episodes: list[Episode], tmp_path: Path) -> TestClient:
    """Create test client with mocked data."""
    from castex.storage import save_episodes

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    save_episodes(sample_episodes, data_dir)

    with patch.dict("os.environ", {"CASTEX_DATA_DIR": str(data_dir)}):
        from castex.server import create_app

        app = create_app()
        return TestClient(app)


def test_index_page(client: TestClient) -> None:
    """Test the index page loads."""
    response = client.get("/")

    assert response.status_code == 200
    assert "Search" in response.text


def test_search_html(client: TestClient) -> None:
    """Test HTML search endpoint."""
    response = client.get("/search?q=Malta")

    assert response.status_code == 200
    assert "Siege of Malta" in response.text
    assert "1 result" in response.text


def test_search_api(client: TestClient) -> None:
    """Test JSON API search endpoint."""
    response = client.get("/api/search?q=Malta")

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == "siege-malta"


def test_episode_detail(client: TestClient) -> None:
    """Test episode detail page."""
    response = client.get("/episode/siege-malta")

    assert response.status_code == 200
    assert "The Siege of Malta" in response.text
    assert "Ottoman siege" in response.text
    assert "History" in response.text


def test_episode_not_found(client: TestClient) -> None:
    """Test 404 for non-existent episode."""
    response = client.get("/episode/nonexistent")

    assert response.status_code == 404


def test_search_api_includes_reading_list(tmp_path: Path) -> None:
    """Test that API response includes reading_list."""
    from unittest.mock import patch

    from castex.storage import save_episodes

    episodes = [
        Episode(
            id="emily-dickinson",
            title="Emily Dickinson",
            broadcast_date=date(2017, 5, 4),
            contributors=["Fiona Green"],
            description="American poet",
            source_url="https://www.bbc.co.uk/programmes/b08p3jlw",
            categories=["Literature"],
            braggoscope_url=None,
            reading_list=[
                "Christopher Benfey, A Summer of Hummingbirds (Penguin Books, 2009)",
            ],
        ),
    ]

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    save_episodes(episodes, data_dir)

    with patch.dict("os.environ", {"CASTEX_DATA_DIR": str(data_dir)}):
        from castex.server import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/api/search?q=Dickinson")

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["reading_list"] == [
            "Christopher Benfey, A Summer of Hummingbirds (Penguin Books, 2009)",
        ]
