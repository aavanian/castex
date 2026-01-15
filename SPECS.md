# Claude Code Prompt: Curated Podcast Episode Search

## Project Overview

Build a searchable archive for podcasts like BBC Radio 4's "In Our Time". The system scrapes episode metadata from Wikipedia and BBC, classifies episodes using an LLM, and provides both a web interface and JSON API for search.

Additional podcasts will be added on a ad-hoc basis.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Wikipedia     │────▶│   JSON files    │────▶│   FastAPI       │
│   (episode      │      │   (episodes.json│      │   server        │
│    list)        │      │    + index)     │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        ▲                    │
        │ (new only)              │                    ├── GET / (search form)
        ▼                        │                    ├── GET /search (HTML)
┌─────────────────┐      ┌──-─────┴───────┐            ├── GET /api/search (JSON)
│   BBC episode   │────▶│ LLM classifier │            └── GET /episode/{id}
│   pages         │      │ (categories)   │
└─────────────────┘      └───-────────────┘
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
    title: str                   # "The Siege of Malta, 1565"
    broadcast_date: date         # 2017-09-21
    contributors: list[str]      # ["Anne Smith (Oxford)", "John Doe (Cambridge)"]
    description: str | None      # Synopsis from BBC page
    source_url: str                 # https://www.bbc.co.uk/programmes/b0xyz123
    categories: list[str]        # ["History", "Military", "Medieval", "Mediterranean"]
    braggoscope_url: str | None  # https://www.braggoscope.com/episode/...
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
│       │   ├── wikipedia.py   # Parse episode list from Wikipedia
│       │   └── bbc.py         # Fetch episode description from BBC
│       ├── classifier.py      # LLM classification
│       ├── search.py          # Search logic (load JSON → SQLite in-memory → query)
│       ├── storage.py         # Read/write JSON files
│       ├── server.py          # FastAPI app
│       └── templates/
│           ├── base.html
│           ├── index.html     # Search form
│           ├── results.html   # Search results
│           └── episode.html   # Episode detail page
├── data/
│   └── episodes.json          # Persisted episode data
├── tests/
│   ├── conftest.py            # Fixtures
│   ├── fixtures/
│   │   ├── wikipedia_sample.html
│   │   └── bbc_episode_sample.html
│   ├── test_scraper.py
│   ├── test_classifier.py
│   ├── test_search.py
│   └── test_server.py
└── scripts/
    └── update.py              # Entry point for cron job
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

### Scraper: Wikipedia

Source: `https://en.wikipedia.org/wiki/List_of_In_Our_Time_programmes`

The page has tables organized by year. Each row contains:
- Broadcast date (with link to BBC page embedded)
- Title
- Contributors with affiliations

Parse all tables, extract episode data, compare against existing `episodes.json` to find new episodes only.

### Scraper: BBC

For each new episode, fetch the BBC page to extract:
- Description/synopsis
- Construct braggoscope URL from episode slug

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

  1. Load `episodes.json`
  2. Create in-memory SQLite database with FTS5 virtual table
  3. Index title, description, contributors, categories

Query logic:

  * If query contains only alphanumeric and spaces: split into terms, OR them together for FTS
  * Future: support +tag -tag syntax

Return results sorted by relevance (FTS rank), limited to 50.

### Server

  * `GET /` - Search form
  * `GET /search?q=...` - HTML results (POST also supported for form submission)
  * `GET /api/search?q=...` - JSON results (same logic, different serialization)
  * `GET /episode/{id}` - Episode detail page

Templates use minimal CSS (inline in base.html or single small file). No external dependencies. Progressive enhancement note: add TODO comment for future JS real-time search.

### Update Script

`scripts/update.py`:

  1. Scrape Wikipedia for full episode list
  2. Compare with stored episodes to find new ones
  3. For each new episode:
     * Fetch BBC page for description
     * Classify with LLM
     * Add to episodes list
  4. Save updated episodes.json

Idempotent and safe to run repeatedly.

## Testing Requirements

### Unit Tests

  * `test_scraper.py`:
    * Parse Wikipedia HTML fixture → list of episodes
    * Parse BBC episode HTML fixture → description
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

# Run update (scrape new episodes)
uv run python scripts/update.py
```

## Out of Scope for v1

  * JavaScript real-time search (TODO noted in templates)
  * Contributor pivot (click contributor to see all their episodes)
  * Reading list extraction from BBC (link to Braggoscope instead)
  * Multiple podcast sources (architecture supports it, not implemented)
  * Semantic/embedding search

## Notes

  * Be defensive with external sources - Wikipedia and BBC page structure may change
  * Add logging throughout for debugging scraper issues
  * Keep the codebase simple and readable over clever
