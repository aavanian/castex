# Claude Code Prompt: Curated Podcast Episode Search

## Project Overview

Build a searchable archive for podcasts like BBC Radio 4's "In Our Time". The system fetches episode metadata from RSS feeds, enriches it with data from source pages, classifies episodes using an LLM, and provides both a web interface and JSON API for search.

Additional podcasts can be added via the provider architecture.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   RSS Feed      │────▶│   JSON files    │────▶│   FastAPI       │
│   (episode      │      │   (per podcast) │      │   server        │
│    list)        │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        ▲                    │
        │ parse HTML             │                    ├── GET / (search form)
        ▼ description            │                    ├── GET /search (HTML)
┌─────────────────┐      ┌───────┴───────┐            ├── GET /api/search (JSON)
│  RSS description│────▶│ LLM classifier │            └── GET /episode/{id}
│  (contributors, │      │ (categories)   │
│   reading list) │      └────────────────┘
└─────────────────┘
        │
        │ fallback only
        ▼
┌─────────────────┐
│   Source page   │
│   (BBC, etc.)   │
└─────────────────┘
```

## Tech Stack

**Language**: Python 3.11+ with type hints throughout
**Package manager**: uv
**Web framework**: FastAPI with Jinja2 templates
**HTTP client**: httpx
**HTML parsing**: beautifulsoup4
**Testing**: pytest with fixtures
**LLM**: OpenAI-compatible API (configurable base URL for Ollama/OpenRouter)

## Data Model

```python

@dataclass
class Episode:
    id: str                      # Slug from title, e.g. "the-siege-of-malta-1565"
    podcast_id: str              # "in_our_time"
    title: str                   # "The Siege of Malta, 1565"
    broadcast_date: date         # 2017-09-21
    contributors: list[str]      # ["Anne Smith (Oxford)", "John Doe (Cambridge)"]
    description: str | None      # Synopsis from RSS or source page
    source_url: str              # https://www.bbc.co.uk/programmes/b0xyz123
    categories: list[str]        # ["History", "Military", "Medieval", "Mediterranean"]
    braggoscope_url: str | None  # https://www.braggoscope.com/episode/...
    reading_list: list[str]      # ["Book Title (Publisher, Year)", ...]
```

## Category Taxonomy

Use flat tags, not hierarchical. Classify each episode with multiple tags from:

**Discipline**: History, Philosophy, Science, Mathematics, Literature, Poetry, Religion, Theology, Art, Architecture, Music, Politics, Economics, Law, Medicine, Technology, Archaeology, Linguistics, Psychology

**Era**: Ancient, Classical, Medieval, Renaissance, Early Modern, Enlightenment, 19th Century, 20th Century, Contemporary

**Region**: Britain, Ireland, France, Germany, Italy, Greece, Rome, Spain, Netherlands, Scandinavia, Eastern Europe, Russia, Middle East, Persia, India, China, Japan, Africa, Americas

The LLM should assign 3-7 tags per episode based on title and description.

## File Structure

```
castex/
├── pyproject.toml
├── README.md
├── src/
│   └── castex/
│       ├── __init__.py
│       ├── config.py          # Settings via environment variables
│       ├── models.py          # Episode dataclass, type definitions
│       ├── scraper/
│       │   ├── __init__.py
│       │   └── bbc.py         # Parse BBC page/RSS description HTML
│       ├── podcasts/
│       │   ├── __init__.py
│       │   ├── base.py        # Protocol definitions
│       │   ├── registry.py    # Provider registry
│       │   └── in_our_time/   # Example podcast implementation
│       │       ├── __init__.py
│       │       ├── feed.py    # RSS feed parser
│       │       └── enricher.py # BBC page enricher
│       ├── classifier.py      # LLM classification
│       ├── search.py          # Search logic
│       ├── db.py              # SQLite database operations
│       ├── storage.py         # Read/write JSON files
│       ├── server.py          # FastAPI app
│       └── templates/
│           ├── base.html
│           ├── index.html     # Search form
│           ├── results.html   # Search results
│           └── episode.html   # Episode detail page
├── data/
│   ├── in_our_time.json       # Cached RSS feed items
│   └── episodes.db            # SQLite database
├── tests/
│   ├── conftest.py            # Fixtures
│   ├── fixtures/
│   │   ├── bbc_episode_sample.html
│   │   └── bbc_episode_new_format.html
│   ├── test_scraper.py
│   ├── test_classifier.py
│   ├── test_search.py
│   └── test_server.py
└── scripts/
    ├── fetch_feed.py          # Fetch and cache RSS feed
    └── update_db.py           # Process feed items into database
```

## Configuration

Environment variables (with defaults):
```
CASTEX_DATA_DIR=./data
CASTEX_LLM_BASE_URL=http://localhost:11434/v1  # Ollama default
CASTEX_LLM_API_KEY=                            # Empty for Ollama
CASTEX_LLM_MODEL=llama3.2
CASTEX_SERVER_HOST=0.0.0.0
CASTEX_SERVER_PORT=8000
```

## Key Implementation Details

### RSS-First Architecture

The primary data source is the podcast's RSS feed, which typically contains:
- Episode title
- Publication date
- Link to source page
- Description (often HTML with structured data)

For many podcasts (like BBC's In Our Time), the RSS description HTML contains structured information including contributors and reading lists in `<p>` tags. The system parses this HTML directly, avoiding HTTP requests to source pages.

### Feed Provider Protocol

Each podcast implements the `FeedProvider` protocol:

```python
class FeedProvider(Protocol):
    def fetch_current_feed(self) -> list[FeedItem]:
        """Fetch and parse the current RSS feed."""
        ...

    def fetch_historic_feed(self) -> list[FeedItem]:
        """One-time scrape for historic episodes not in RSS."""
        ...

    def is_feed_complete(self) -> bool:
        """Check if RSS feed contains full history."""
        ...
```

### Episode Enricher Protocol

Optional enricher for additional metadata:

```python
class EpisodeEnricher(Protocol):
    async def enrich(self, item: FeedItem) -> dict[str, Any]:
        """Fetch additional data for an episode."""
        ...
```

The enricher is only called as a fallback when RSS description parsing doesn't yield contributors.

### Scraper: RSS Description

The `parse_rss_description_html()` function extracts structured data from RSS description HTML:

- **New format**: Multiple `<p>` tags with "With" separator, contributor paragraphs, "Reading list:" marker
- **Old format**: Single paragraph with "With Name, Title; Name, Title." at end

### Scraper: Source Page (Fallback)

For episodes where RSS description parsing fails, fetch the source page to extract:
- Description/synopsis
- Contributors
- Reading list

Handle rate limiting gracefully (add delays between requests).

### Classifier

Single LLM call per episode. Prompt structure:

```
Classify this podcast episode into categories.

Title: {title}
Description: {description}
Contributors: {contributors}

Assign 3-7 tags from these options:
- Discipline: History, Philosophy, Science, ...
- Era: Ancient, Classical, Medieval, ...
- Region: Britain, France, Greece, ...

Return only a JSON array of tag strings, e.g. ["History", "Medieval", "France"]
```

Use temperature=0 for consistency. Parse JSON from response, validate against known tags.

### Search

On server startup:

  1. Load episodes from SQLite database
  2. Use FTS5 virtual table for full-text search
  3. Index title, description, contributors, categories, reading list

Query logic:

  * If query contains only alphanumeric and spaces: split into terms, OR them together for FTS
  * Future: support +tag -tag syntax

Return results sorted by relevance (FTS rank), limited to 50.

### Server

  * `GET /` - Search form
  * `GET /search?q=...` - HTML results (POST also supported for form submission)
  * `GET /api/search?q=...` - JSON results (same logic, different serialization)
  * `GET /episode/{id}` - Episode detail page

Templates use minimal CSS (inline in base.html or single small file). No external dependencies.

### Update Workflow

Two-step process:

1. `scripts/fetch_feed.py`: Fetch RSS feed and save to JSON
2. `scripts/update_db.py`: Process new feed items into database
   - Parse RSS description HTML for contributors/reading list
   - Fall back to source page enrichment if needed
   - Classify with LLM
   - Save to SQLite

Both scripts are idempotent and safe to run repeatedly.

## Testing Requirements

### Unit Tests

  * `test_scraper.py`:
    * Parse BBC episode HTML fixture → description, contributors, reading list
    * Parse RSS description HTML → structured data
    * Handle malformed/missing data
  * `test_classifier.py`:
    * Mock LLM response → parsed categories
    * Invalid JSON response → graceful fallback
    * Empty/missing description → still works
  * `test_search.py`:
    * Load episodes → build index → query returns expected results
    * Empty query → returns nothing or everything (decide)
    * Multi-term query → OR behavior

### Integration Tests

  * `test_server.py`:
    * Start server with fixture data
    * Test each endpoint returns expected status and content
    * Test search form submission flow

## Development Workflow

```bash
# Setup
uv venv
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run server locally
uv run python -m castex.server

# Fetch RSS feed
uv run python scripts/fetch_feed.py

# Update database with new episodes
uv run python scripts/update_db.py
```

## Out of Scope for v1

  * JavaScript real-time search (TODO noted in templates)
  * Contributor pivot (click contributor to see all their episodes)
  * Semantic/embedding search

## Notes

  * Be defensive with external sources - RSS and page structure may change
  * Add logging throughout for debugging scraper issues
  * Keep the codebase simple and readable over clever
