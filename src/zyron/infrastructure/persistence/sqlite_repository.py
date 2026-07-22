import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class SQLiteRepository:
    def __init__(self, database_path: str = "data/zyron.db") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self._create_tables()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row

        return connection

    def _create_tables(self) -> None:
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_text TEXT NOT NULL,
            assistant_text TEXT NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """

        with self._connect() as connection:
            connection.executescript(create_tables_sql)

    def save_memory(self, key: str, value: str) -> None:
        now = self._current_datetime()

        query = """
        INSERT INTO memories (
            key,
            value,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at;
        """

        with self._connect() as connection:
            connection.execute(
                query,
                (key, value, now, now),
            )

    def get_memory(self, key: str) -> str | None:
        query = """
        SELECT value
        FROM memories
        WHERE key = ?;
        """

        with self._connect() as connection:
            result = connection.execute(
                query,
                (key,),
            ).fetchone()

        if result is None:
            return None

        return str(result["value"])

    def delete_memory(self, key: str) -> bool:
        query = """
        DELETE FROM memories
        WHERE key = ?;
        """

        with self._connect() as connection:
            cursor = connection.execute(
                query,
                (key,),
            )

        return cursor.rowcount > 0

    def list_memories(self) -> list[dict[str, str]]:
        query = """
        SELECT key, value, created_at, updated_at
        FROM memories
        ORDER BY updated_at DESC;
        """

        with self._connect() as connection:
            results = connection.execute(query).fetchall()

        return [
            {
                "key": str(row["key"]),
                "value": str(row["value"]),
                "created_at": str(row["created_at"]),
                "updated_at": str(row["updated_at"]),
            }
            for row in results
        ]

    def save_interaction(
        self,
        user_text: str,
        assistant_text: str,
        source: str = "text",
    ) -> None:
        query = """
        INSERT INTO interactions (
            user_text,
            assistant_text,
            source,
            created_at
        )
        VALUES (?, ?, ?, ?);
        """

        with self._connect() as connection:
            connection.execute(
                query,
                (
                    user_text,
                    assistant_text,
                    source,
                    self._current_datetime(),
                ),
            )

    def get_recent_interactions(
        self,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        query = """
        SELECT
            user_text,
            assistant_text,
            source,
            created_at
        FROM interactions
        ORDER BY id DESC
        LIMIT ?;
        """

        with self._connect() as connection:
            results = connection.execute(
                query,
                (limit,),
            ).fetchall()

        return [
            {
                "user_text": str(row["user_text"]),
                "assistant_text": str(row["assistant_text"]),
                "source": str(row["source"]),
                "created_at": str(row["created_at"]),
            }
            for row in reversed(results)
        ]

    @staticmethod
    def _current_datetime() -> str:
        return datetime.now(timezone.utc).isoformat()
