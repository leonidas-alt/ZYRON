from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


logger = logging.getLogger(__name__)


class SQLiteRepository:
    DEFAULT_DATABASE_PATH = Path("data/zyron.db")

    def __init__(
        self,
        database_path: str | Path = DEFAULT_DATABASE_PATH,
    ) -> None:
        self._database_path = Path(database_path)
        self._prepare_database_directory()
        self.initialize()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_text TEXT NOT NULL,
                    assistant_text TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'unknown',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_memories_key
                ON memories(key);

                CREATE INDEX IF NOT EXISTS idx_interactions_created_at
                ON interactions(created_at);
                """
            )

            connection.commit()

        logger.info(
            "Banco SQLite inicializado em: %s",
            self._database_path,
        )

    def save_memory(
        self,
        key: str,
        value: str,
    ) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO memories (
                    key,
                    value
                )
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    key,
                    value,
                ),
            )

            connection.commit()

        logger.debug(
            "Memória persistida no SQLite: key=%s",
            key,
        )

    def get_memory(
        self,
        key: str,
    ) -> dict[str, Any] | None:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    key,
                    value,
                    created_at,
                    updated_at
                FROM memories
                WHERE key = ?
                LIMIT 1
                """,
                (key,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def delete_memory(
        self,
        key: str,
    ) -> bool:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE key = ?
                """,
                (key,),
            )

            connection.commit()

            deleted = cursor.rowcount > 0

        if deleted:
            logger.debug(
                "Memória removida do SQLite: key=%s",
                key,
            )

        return deleted

    def list_memories(
        self,
    ) -> list[dict[str, Any]]:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    key,
                    value,
                    created_at,
                    updated_at
                FROM memories
                ORDER BY updated_at DESC, key ASC
                """
            )

            rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def count_memories(self) -> int:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM memories
                """
            )

            row = cursor.fetchone()

        if row is None:
            return 0

        return int(row["total"])

    def clear_memories(self) -> int:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM memories
                """
            )

            connection.commit()

            deleted_count = cursor.rowcount

        logger.warning(
            "Todas as memórias foram removidas. Total=%d",
            deleted_count,
        )

        return deleted_count

    def save_interaction(
        self,
        user_text: str,
        assistant_text: str,
        source: str = "unknown",
    ) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO interactions (
                    user_text,
                    assistant_text,
                    source
                )
                VALUES (?, ?, ?)
                """,
                (
                    user_text,
                    assistant_text,
                    source,
                ),
            )

            connection.commit()

        logger.debug(
            "Interação salva no histórico: source=%s",
            source,
        )

    def list_interactions(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        if limit <= 0:
            return []

        with self._connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    user_text,
                    assistant_text,
                    source,
                    created_at
                FROM interactions
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )

            rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_recent_interactions(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        interactions = self.list_interactions(limit)

        interactions.reverse()

        return interactions

    def count_interactions(self) -> int:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM interactions
                """
            )

            row = cursor.fetchone()

        if row is None:
            return 0

        return int(row["total"])

    def clear_interactions(self) -> int:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM interactions
                """
            )

            connection.commit()

            deleted_count = cursor.rowcount

        logger.warning(
            "Histórico de interações apagado. Total=%d",
            deleted_count,
        )

        return deleted_count

    def close(self) -> None:
        logger.debug(
            "SQLiteRepository utiliza conexões por operação."
        )

    def health_check(self) -> bool:
        try:
            with self._connection() as connection:
                cursor = connection.execute(
                    """
                    SELECT 1 AS healthy
                    """
                )

                row = cursor.fetchone()

            return row is not None and row["healthy"] == 1

        except sqlite3.Error:
            logger.exception(
                "Falha no health check do SQLite."
            )

            return False

    def _prepare_database_directory(self) -> None:
        if str(self._database_path) == ":memory:":
            return

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    @contextmanager
    def _connection(
        self,
    ) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            self._database_path,
            timeout=10,
        )

        connection.row_factory = sqlite3.Row

        try:
            connection.execute(
                """
                PRAGMA foreign_keys = ON
                """
            )

            connection.execute(
                """
                PRAGMA journal_mode = WAL
                """
            )

            yield connection

        except sqlite3.Error:
            connection.rollback()

            logger.exception(
                "Erro durante uma operação no banco SQLite."
            )

            raise

        finally:
            connection.close()
