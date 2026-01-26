"""SQLite database for episode storage and search."""

import json
import sqlite3
from datetime import date
from pathlib import Path

from castex.models import Episode

MAX_SEARCH_RESULTS = 50


class Database:
    """SQLite database for episode storage with FTS5 search."""

    def __init__(self, db_path: Path) -> None:
        """Initialize the database, creating tables if needed."""
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        """Create the database tables if they don't exist."""
        cursor = self._conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id TEXT PRIMARY KEY,
                podcast_id TEXT NOT NULL,
                title TEXT NOT NULL,
                broadcast_date TEXT NOT NULL,
                source_url TEXT NOT NULL,
                contributors TEXT,
                description TEXT,
                categories TEXT,
                braggoscope_url TEXT,
                reading_list TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_episodes_podcast ON episodes(podcast_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_episodes_date ON episodes(broadcast_date)
        """)

        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
                id,
                title,
                description,
                contributors,
                categories,
                reading_list,
                tokenize='trigram'
            )
        """)

        self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    def upsert_episode(self, episode: Episode) -> None:
        """Insert or update an episode."""
        cursor = self._conn.cursor()

        cursor.execute(
            """
            INSERT INTO episodes (
                id, podcast_id, title, broadcast_date, source_url,
                contributors, description, categories, braggoscope_url,
                reading_list, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                podcast_id = excluded.podcast_id,
                title = excluded.title,
                broadcast_date = excluded.broadcast_date,
                source_url = excluded.source_url,
                contributors = excluded.contributors,
                description = excluded.description,
                categories = excluded.categories,
                braggoscope_url = excluded.braggoscope_url,
                reading_list = excluded.reading_list,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                episode.id,
                episode.podcast_id,
                episode.title,
                episode.broadcast_date.isoformat(),
                episode.source_url,
                json.dumps(episode.contributors),
                episode.description,
                json.dumps(episode.categories),
                episode.braggoscope_url,
                json.dumps(episode.reading_list),
            ),
        )

        cursor.execute(
            "DELETE FROM episodes_fts WHERE id = ?",
            (episode.id,),
        )

        cursor.execute(
            """
            INSERT INTO episodes_fts (id, title, description, contributors, categories, reading_list)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                episode.id,
                episode.title,
                episode.description or "",
                " ".join(episode.contributors),
                " ".join(episode.categories),
                " ".join(episode.reading_list),
            ),
        )

        self._conn.commit()

    def get_episode(self, episode_id: str) -> Episode | None:
        """Get an episode by ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_episode(row)

    def get_all_episodes(self) -> list[Episode]:
        """Get all episodes, sorted by broadcast date descending."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM episodes ORDER BY broadcast_date DESC")
        return [self._row_to_episode(row) for row in cursor.fetchall()]

    def get_episodes_by_podcast(self, podcast_id: str) -> list[Episode]:
        """Get all episodes for a podcast, sorted by broadcast date descending."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM episodes WHERE podcast_id = ? ORDER BY broadcast_date DESC",
            (podcast_id,),
        )
        return [self._row_to_episode(row) for row in cursor.fetchall()]

    def search(self, query: str) -> list[Episode]:
        """Search episodes using FTS5."""
        query = query.strip()
        if not query:
            return []

        terms = query.split()
        fts_query = " OR ".join(terms)

        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT e.* FROM episodes e
            JOIN episodes_fts f ON e.id = f.id
            WHERE episodes_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, MAX_SEARCH_RESULTS),
        )

        return [self._row_to_episode(row) for row in cursor.fetchall()]

    def _row_to_episode(self, row: sqlite3.Row) -> Episode:
        """Convert a database row to an Episode."""
        return Episode(
            id=row["id"],
            podcast_id=row["podcast_id"],
            title=row["title"],
            broadcast_date=date.fromisoformat(row["broadcast_date"]),
            contributors=json.loads(row["contributors"]) if row["contributors"] else [],
            description=row["description"],
            source_url=row["source_url"],
            categories=json.loads(row["categories"]) if row["categories"] else [],
            braggoscope_url=row["braggoscope_url"],
            reading_list=json.loads(row["reading_list"]) if row["reading_list"] else [],
        )
