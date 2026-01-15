"""Tests for configuration module."""

from pathlib import Path

import pytest

from castex.config import Settings


def test_settings_defaults() -> None:
    """Test that Settings has correct default values."""
    settings = Settings()

    assert settings.data_dir == Path("./data")
    assert settings.llm_base_url == "http://localhost:11434/v1"
    assert settings.llm_api_key == ""
    assert settings.llm_model == "llama3.2"
    assert settings.server_host == "0.0.0.0"
    assert settings.server_port == 8000


def test_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Settings loads from environment variables."""
    monkeypatch.setenv("CASTEX_DATA_DIR", "/custom/data")
    monkeypatch.setenv("CASTEX_LLM_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("CASTEX_LLM_API_KEY", "sk-test-key")
    monkeypatch.setenv("CASTEX_LLM_MODEL", "gpt-4")
    monkeypatch.setenv("CASTEX_SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("CASTEX_SERVER_PORT", "3000")

    settings = Settings()

    assert settings.data_dir == Path("/custom/data")
    assert settings.llm_base_url == "https://api.openai.com/v1"
    assert settings.llm_api_key == "sk-test-key"
    assert settings.llm_model == "gpt-4"
    assert settings.server_host == "127.0.0.1"
    assert settings.server_port == 3000
