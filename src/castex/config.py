"""Configuration settings via environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path


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
        self.data_dir = Path(os.environ.get("CASTEX_DATA_DIR", "./data"))
        self.llm_base_url = os.environ.get("CASTEX_LLM_BASE_URL", "http://localhost:11434/v1")
        self.llm_api_key = os.environ.get("CASTEX_LLM_API_KEY", "")
        self.llm_model = os.environ.get("CASTEX_LLM_MODEL", "gemma3:4b-it-qat")
        self.server_host = os.environ.get("CASTEX_SERVER_HOST", "0.0.0.0")
        self.server_port = int(os.environ.get("CASTEX_SERVER_PORT", "8000"))
