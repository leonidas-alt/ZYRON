from __future__ import annotations
import asyncio
from pathlib import Path
import sqlite3
from datetime import UTC, datetime
from core.models import Interaction
from core.ports import InteractionRepository


class SQLiteRepository(InteractionRepository):

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    async def initialize(self) -> None:
        await asyncio.to_thread(self._initialize)

    async def save_interaction(self, user_text: str, assistant_text: str) -> None:
        await asyncio.to_thread(self._save_interaction, user_text, assistant_text)

    async def get_recent_interactions(self, limit: int = 5) -> list[Interaction]:
        return await asyncio.to_thread(self._get_recent_interactions, limit)

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

    def _get_recent_interactions(self, limit: int = 5) -> list[Interaction]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT user_text, assistant_text, created_at
                FROM interactions
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        interactions: list[Interaction] = []
        for user_text, assistant_text, created_at in reversed(rows):
            interactions.append(
                Interaction(
                    user_text=user_text,
                    assistant_text=assistant_text,
                    created_at=self._parse_created_at(str(created_at)),
                )
            )
        return interactions

    def _parse_created_at(self, value: str) -> datetime:
        try:
            return datetime.fromisoformat(value).replace(tzinfo=UTC)
        except ValueError:
            return datetime.now(UTC)
