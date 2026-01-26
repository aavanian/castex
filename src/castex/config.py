"""Configuration settings via environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

# Default values - used by Settings and tests
DEFAULT_DATA_DIR = "./data"
DEFAULT_LLM_BASE_URL = "http://localhost:11434/v1"
DEFAULT_LLM_API_KEY = ""
DEFAULT_LLM_MODEL = "gemma3:4b-it-qat"
DEFAULT_SERVER_HOST = "0.0.0.0"
DEFAULT_SERVER_PORT = 8000


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    data_dir: Path
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    server_host: str
    server_port: int

    def __init__(self) -> None:
        """Initialize settings from environment variables with defaults."""
        self.data_dir = Path(os.environ.get("CASTEX_DATA_DIR", DEFAULT_DATA_DIR))
        self.llm_base_url = os.environ.get("CASTEX_LLM_BASE_URL", DEFAULT_LLM_BASE_URL)
        self.llm_api_key = os.environ.get("CASTEX_LLM_API_KEY", DEFAULT_LLM_API_KEY)
        self.llm_model = os.environ.get("CASTEX_LLM_MODEL", DEFAULT_LLM_MODEL)
        self.server_host = os.environ.get("CASTEX_SERVER_HOST", DEFAULT_SERVER_HOST)
        self.server_port = int(os.environ.get("CASTEX_SERVER_PORT", str(DEFAULT_SERVER_PORT)))

    @property
    def db_path(self) -> Path:
        """Path to the SQLite database."""
        return self.data_dir / "episodes.db"

    def feed_json_path(self, podcast_id: str) -> Path:
        """Path to the feed JSON file for a podcast."""
        return self.data_dir / f"{podcast_id}_feed.json"

    def historic_feed_json_path(self, podcast_id: str) -> Path:
        """Path to the historic feed JSON backup for a podcast."""
        return self.data_dir / f"{podcast_id}_historic_feed.json"
