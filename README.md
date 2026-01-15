# In Our Time Archive

Searchable index for episode of podcasts like BBC Radio 4's "In Our Time".

## Features

- Scrapes episode metadata from Wikipedia and BBC
- Classifies episodes using an LLM
- Full-text search with SQLite FTS5
- Web interface and JSON API

## Setup

```bash
# Install dependencies
uv venv
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run server
uv run python -m castex.server

# Update episodes (scrape new ones)
uv run python scripts/update.py
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CASTEX_DATA_DIR` | `./data` | Directory for episode data |
| `CASTEX_LLM_BASE_URL` | `http://localhost:11434/v1` | LLM API base URL |
| `CASTEX_LLM_API_KEY` | (empty) | LLM API key |
| `CASTEX_LLM_MODEL` | `llama3.2` | LLM model name |
| `CASTEX_SERVER_HOST` | `0.0.0.0` | Server host |
| `CASTEX_SERVER_PORT` | `8000` | Server port |
