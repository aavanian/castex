"""Tests for configuration module."""

from pathlib import Path

import pytest

from castex.config import (
    DEFAULT_DATA_DIR,
    DEFAULT_LLM_API_KEY,
    DEFAULT_LLM_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    Settings,
)


def test_settings_defaults() -> None:
    """Test that Settings has correct default values."""
    settings = Settings()

    assert settings.data_dir == Path(DEFAULT_DATA_DIR)
    assert settings.llm_base_url == DEFAULT_LLM_BASE_URL
    assert settings.llm_api_key == DEFAULT_LLM_API_KEY
    assert settings.llm_model == DEFAULT_LLM_MODEL
    assert settings.server_host == DEFAULT_SERVER_HOST
    assert settings.server_port == DEFAULT_SERVER_PORT


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
