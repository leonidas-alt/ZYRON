from __future__ import annotations

import asyncio
from pathlib import Path
import sqlite3

from core.ports import InteractionRepository


class SQLiteRepository(InteractionRepository):
    """SQLite persistence adapter using context managers for connection safety."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    async def initialize(self) -> None:
        await asyncio.to_thread(self._initialize)

    async def save_interaction(self, user_text: str, assistant_text: str) -> None:
        await asyncio.to_thread(self._save_interaction, user_text, assistant_text)

    def _initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_text TEXT NOT NULL,
                    assistant_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _save_interaction(self, user_text: str, assistant_text: str) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "INSERT INTO interactions (user_text, assistant_text) VALUES (?, ?)",
                (user_text, assistant_text),
            )
