"""Full-text search using SQLite FTS5."""

import sqlite3

from castex.models import Episode

MAX_RESULTS = 50


class SearchIndex:
    """In-memory full-text search index for episodes."""

    def __init__(self, episodes: list[Episode]) -> None:
        """Create a search index from a list of episodes."""
        self._episodes = {ep.id: ep for ep in episodes}
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._build_index(episodes)

    def _build_index(self, episodes: list[Episode]) -> None:
        """Build the FTS5 index from episodes."""
        cursor = self._conn.cursor()

        cursor.execute("""
            CREATE VIRTUAL TABLE episodes_fts USING fts5(
                id,
                title,
                description,
                contributors,
                categories,
                tokenize='porter unicode61'
            )
        """)

        for ep in episodes:
            cursor.execute(
                """
                INSERT INTO episodes_fts (id, title, description, contributors, categories)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ep.id,
                    ep.title,
                    ep.description or "",
                    " ".join(ep.contributors),
                    " ".join(ep.categories),
                ),
            )

        self._conn.commit()

    def search(self, query: str) -> list[Episode]:
        """Search for episodes matching the query.

        Terms are ORed together. Results are sorted by relevance.
        """
        query = query.strip()
        if not query:
            return []

        # Split into terms and join with OR
        terms = query.split()
        fts_query = " OR ".join(terms)

        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT id FROM episodes_fts
            WHERE episodes_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, MAX_RESULTS),
        )

        results = []
        for (episode_id,) in cursor.fetchall():
            if episode_id in self._episodes:
                results.append(self._episodes[episode_id])

        return results
