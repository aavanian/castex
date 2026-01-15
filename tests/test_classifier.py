"""Tests for LLM classifier module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from castex.classifier import classify_episode


@pytest.mark.asyncio
async def test_classify_episode() -> None:
    """Test classifying an episode with mocked LLM response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '["History", "Medieval", "Mediterranean"]'

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("castex.classifier.AsyncOpenAI", return_value=mock_client):
        categories = await classify_episode(
            title="The Siege of Malta, 1565",
            description="Discussion about the Ottoman siege of Malta.",
            contributors=["Prof. A (Oxford)", "Dr. B (Cambridge)"],
            base_url="http://localhost:11434/v1",
            api_key="",
            model="llama3.2",
        )

    assert categories == ["History", "Medieval", "Mediterranean"]


@pytest.mark.asyncio
async def test_classify_episode_invalid_json() -> None:
    """Test handling of invalid JSON response from LLM."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "not valid json"

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("castex.classifier.AsyncOpenAI", return_value=mock_client):
        categories = await classify_episode(
            title="Test Episode",
            description="Test description",
            contributors=[],
            base_url="http://localhost:11434/v1",
            api_key="",
            model="llama3.2",
        )

    assert categories == []


@pytest.mark.asyncio
async def test_classify_episode_no_description() -> None:
    """Test classifying episode with no description."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '["Philosophy", "Ancient"]'

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("castex.classifier.AsyncOpenAI", return_value=mock_client):
        categories = await classify_episode(
            title="Plato's Republic",
            description=None,
            contributors=["Prof. X"],
            base_url="http://localhost:11434/v1",
            api_key="",
            model="llama3.2",
        )

    assert categories == ["Philosophy", "Ancient"]
