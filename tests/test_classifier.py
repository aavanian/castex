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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_classify_episode_integration() -> None:
    """Integration test that calls a real LLM using configured settings."""
    import httpx

    from castex.config import Settings

    settings = Settings()

    # Check if LLM server is available and model exists
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.llm_base_url}/models", timeout=5.0)
            if response.status_code != 200:
                pytest.skip(f"LLM not available at {settings.llm_base_url}")

            # Check if configured model exists
            models_data = response.json()
            model_ids = [m.get("id", "") for m in models_data.get("data", [])]
            if settings.llm_model not in model_ids:
                pytest.skip(f"Model '{settings.llm_model}' not available (have: {model_ids})")
    except (httpx.ConnectError, httpx.TimeoutException):
        pytest.skip(f"LLM not available at {settings.llm_base_url}")

    categories = await classify_episode(
        title="The French Revolution",
        description="Discussion of the causes and consequences of the French Revolution.",
        contributors=["Prof. History (Oxford)"],
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
    )

    assert isinstance(categories, list)
    assert len(categories) > 0
    assert all(isinstance(c, str) for c in categories)
