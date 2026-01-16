"""FastAPI web server for episode search."""

from pathlib import Path
from typing import Any, Protocol

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from castex.config import Settings
from castex.models import Episode
from castex.search import DatabaseSearchIndex, SearchIndex
from castex.storage import load_episodes

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


class EpisodeSource(Protocol):
    """Protocol for episode data sources."""

    def search(self, query: str) -> list[Episode]: ...
    def get_episode(self, episode_id: str) -> Episode | None: ...


class JsonEpisodeSource:
    """Episode source backed by in-memory index from JSON."""

    def __init__(self, episodes: list[Episode]) -> None:
        """Create source from episode list."""
        self._search_index = SearchIndex(episodes)
        self._episodes_by_id = {ep.id: ep for ep in episodes}

    def search(self, query: str) -> list[Episode]:
        """Search episodes."""
        return self._search_index.search(query)

    def get_episode(self, episode_id: str) -> Episode | None:
        """Get episode by ID."""
        return self._episodes_by_id.get(episode_id)


def _create_episode_source(settings: Settings) -> EpisodeSource:
    """Create the best available episode source.

    Prefers SQLite database if available, falls back to JSON storage.
    """
    if settings.db_path.exists():
        return DatabaseSearchIndex(settings.db_path)

    episodes = load_episodes(settings.data_dir)
    return JsonEpisodeSource(episodes)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="CastEx", description="Podcast Episode Search")

    settings = Settings()
    episode_source = _create_episode_source(settings)

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        """Render the search form."""
        return templates.TemplateResponse(request, "index.html")

    @app.get("/search", response_class=HTMLResponse)
    async def search_html(request: Request, q: str = "") -> HTMLResponse:
        """Search episodes and return HTML results."""
        results = episode_source.search(q)
        return templates.TemplateResponse(
            request,
            "results.html",
            {"query": q, "episodes": results},
        )

    @app.get("/api/search")
    async def search_api(q: str = "") -> dict[str, Any]:
        """Search episodes and return JSON results."""
        results = episode_source.search(q)
        return {
            "query": q,
            "count": len(results),
            "results": [_episode_to_dict(ep) for ep in results],
        }

    @app.get("/episode/{episode_id}", response_class=HTMLResponse)
    async def episode_detail(request: Request, episode_id: str) -> HTMLResponse:
        """Render episode detail page."""
        episode = episode_source.get_episode(episode_id)
        if not episode:
            raise HTTPException(status_code=404, detail="Episode not found")
        return templates.TemplateResponse(
            request,
            "episode.html",
            {"episode": episode},
        )

    return app


def _episode_to_dict(episode: Episode) -> dict[str, Any]:
    """Convert Episode to dictionary for JSON response."""
    return {
        "id": episode.id,
        "podcast_id": episode.podcast_id,
        "title": episode.title,
        "broadcast_date": episode.broadcast_date.isoformat(),
        "contributors": episode.contributors,
        "description": episode.description,
        "source_url": episode.source_url,
        "categories": episode.categories,
        "braggoscope_url": episode.braggoscope_url,
        "reading_list": episode.reading_list,
    }


# Entry point for running with uvicorn
app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = Settings()
    uvicorn.run(
        "castex.server:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
    )
