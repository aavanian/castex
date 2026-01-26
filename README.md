# Castex - Podcast Episode Search

Searchable index for episodes of podcasts like BBC Radio 4's "In Our Time".

## Features

- Fetches episode metadata from RSS feeds
- Parses structured data (contributors, reading lists) from RSS description HTML
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

## Workflow

The system uses an RSS-first architecture:

1. **Fetch RSS feed** - Download the podcast's RSS feed and cache it as JSON
2. **Parse RSS description** - Extract contributors and reading lists from description HTML
3. **Fallback enrichment** - If RSS parsing fails, fetch the source page for metadata
4. **Classify** - Use LLM to assign category tags
5. **Store** - Save episodes to SQLite database
6. **Serve** - Provide search via web UI and JSON API

### Updating Episodes

```bash
# Step 1: Fetch RSS feed for all registered podcasts
uv run python scripts/fetch_feed.py

# Step 2: Process new episodes into the database
uv run python scripts/update_db.py
```

Both scripts are idempotent and safe to run repeatedly (e.g., via cron).

## Adding a New Podcast Provider

The system supports multiple podcasts through a provider architecture. Each podcast needs:

1. A **Feed Provider** - fetches and parses the RSS feed
2. An **Enricher** (optional) - fetches additional metadata from source pages

### Step 1: Create the Provider Module

Create a new directory under `src/castex/podcasts/`:

```
src/castex/podcasts/
└── my_podcast/
    ├── __init__.py
    ├── feed.py
    └── enricher.py  # optional
```

### Step 2: Implement the Feed Provider

In `feed.py`, implement the `FeedProvider` protocol:

```python
"""My Podcast RSS feed parser."""

import xml.etree.ElementTree as ET
from datetime import date
from email.utils import parsedate_to_datetime

import httpx

from castex.models import FeedItem

RSS_FEED_URL = "https://example.com/podcast.rss"


def parse_rss_xml(xml_content: str) -> list[FeedItem]:
    """Parse RSS XML content into FeedItems."""
    root = ET.fromstring(xml_content)
    channel = root.find("channel")
    if channel is None:
        return []

    items: list[FeedItem] = []
    for item in channel.findall("item"):
        # Extract guid, title, link, pubDate, description
        # Convert to FeedItem
        items.append(FeedItem(...))

    return items


class MyPodcastFeedProvider:
    """Feed provider for My Podcast."""

    def fetch_current_feed(self) -> list[FeedItem]:
        """Fetch and parse the current RSS feed."""
        response = httpx.get(RSS_FEED_URL, timeout=30.0)
        response.raise_for_status()
        return parse_rss_xml(response.text)

    def fetch_historic_feed(self) -> list[FeedItem]:
        """Return empty list if RSS contains full history."""
        return []

    def is_feed_complete(self) -> bool:
        """Return True if RSS feed contains the complete history."""
        return True
```

### Step 3: Implement the Enricher (Optional)

If the RSS description doesn't contain all needed metadata, create an enricher:

```python
"""My Podcast episode enricher."""

from typing import Any

import httpx

from castex.models import FeedItem


class MyPodcastEnricher:
    """Enriches feed items with data from source pages."""

    async def enrich(self, item: FeedItem) -> dict[str, Any]:
        """Fetch and parse the source page for additional metadata."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(item.link)
                response.raise_for_status()

            # Parse the page HTML to extract:
            # - description (if not in RSS)
            # - contributors
            # - reading_list

            return {
                "description": "...",
                "contributors": ["Name, Title", ...],
                "reading_list": ["Book (Publisher, Year)", ...],
            }

        except httpx.HTTPError:
            return {
                "description": None,
                "contributors": [],
                "reading_list": [],
            }
```

### Step 4: Register the Provider

Add your provider to `src/castex/podcasts/registry.py`:

```python
from castex.podcasts.my_podcast.feed import MyPodcastFeedProvider
from castex.podcasts.my_podcast.enricher import MyPodcastEnricher  # if needed

_FEED_PROVIDERS: dict[str, type[FeedProvider]] = {
    "in_our_time": InOurTimeFeedProvider,
    "my_podcast": MyPodcastFeedProvider,  # Add this
}

_ENRICHERS: dict[str, type[EpisodeEnricher]] = {
    "in_our_time": InOurTimeEnricher,
    "my_podcast": MyPodcastEnricher,  # Add this if needed
}
```

### Step 5: Add Tests

Create tests in `tests/test_my_podcast_feed.py`:

```python
from castex.podcasts.my_podcast.feed import parse_rss_xml

def test_parse_rss_xml(fixtures_dir):
    xml = (fixtures_dir / "my_podcast_sample.rss").read_text()
    items = parse_rss_xml(xml)
    assert len(items) > 0
    assert items[0].title == "Expected Title"
```

## Ideas

- Script to only update classification without fetching episode info again
- Contributor pivot (click contributor to see all their episodes)
- Archive episodes: a quick way would be to link to IA/WBM if it exists. A stronger way would be to actually store the episode but that may raise some copyright/license issues.
- If we store the full transcript of the episodes, we could add semantic/embedding search
- Clickable tags
- Archive/Regenerate full RSS feeds (in case providers truncate them)
