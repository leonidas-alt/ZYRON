from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from domain.models import Interaction, MemoryItem
from domain.ports import MemoryRepository


class SQLiteRepository(MemoryRepository):
    """SQLite implementation for history and persistent memory."""

    def __init__(self, database_path: str = "data/zyron.db") -> None:
        self._path = Path(database_path)

    async def initialize(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS interactions ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_text TEXT NOT NULL, "
                "assistant_text TEXT NOT NULL, "
                "created_at TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS memories ("
                "key TEXT PRIMARY KEY, "
                "value TEXT NOT NULL, "
                "created_at TEXT NOT NULL)"
            )

    async def save_interaction(self, user_text: str, assistant_text: str) -> None:
        await self.initialize()
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                "INSERT INTO interactions (user_text, assistant_text, created_at) "
                "VALUES (?, ?, ?)",
                (user_text, assistant_text, datetime.now(UTC).isoformat()),
            )

    async def get_recent_interactions(self, limit: int = 5) -> list[Interaction]:
        await self.initialize()
        with sqlite3.connect(self._path) as conn:
            rows = conn.execute(
                "SELECT user_text, assistant_text, created_at "
                "FROM interactions ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [Interaction(row[0], row[1], datetime.fromisoformat(row[2])) for row in reversed(rows)]

    async def remember(self, key: str, value: str) -> None:
        await self.initialize()
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO memories (key, value, created_at) VALUES (?, ?, ?)",
                (key, value, datetime.now(UTC).isoformat()),
            )

    async def recall(self, key: str) -> MemoryItem | None:
        await self.initialize()
        with sqlite3.connect(self._path) as conn:
            row = conn.execute(
                "SELECT key, value, created_at FROM memories WHERE key=?",
                (key,),
            ).fetchone()
        if row is None:
            return None
        return MemoryItem(row[0], row[1], datetime.fromisoformat(row[2]))

    async def list_memories(self) -> list[MemoryItem]:
        await self.initialize()
        with sqlite3.connect(self._path) as conn:
            rows = conn.execute(
                "SELECT key, value, created_at FROM memories ORDER BY key"
            ).fetchall()
        return [MemoryItem(row[0], row[1], datetime.fromisoformat(row[2])) for row in rows]

    async def forget(self, key: str) -> bool:
        await self.initialize()
        with sqlite3.connect(self._path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE key=?", (key,))
            return cursor.rowcount > 0
