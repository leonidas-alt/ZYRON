"""
ROADMAP DO MÓDULO

Versão Atual:

* Cria schema SQLite básico e salva interações.

Próxima Versão:

* Adicionar migrações, repositórios especializados e transações explícitas.

Versão Futura:

* PostgreSQL, banco vetorial e criptografia de dados sensíveis.

Dependências Futuras:

* SQLite, PostgreSQL, ChromaDB, pgvector
"""

# TODO:
# Criar testes de inicialização, persistência, consultas e falhas de permissão no arquivo de banco.
# FIXME:
# O schema é criado inline e ainda não possui migrações versionadas.
# IMPROVEMENT:
# Separar repositórios de interações, memórias, aliases, tokens OAuth, preferências e finanças.
# FUTURE:
# Suportar PostgreSQL, ChromaDB, pgvector, criptografia de campos sensíveis e backup local.
# OPTIMIZATION:
# Reutilizar conexões com cuidado ou usar pool quando migrar para PostgreSQL.
# SECURITY:
# Criptografar tokens, e-mails, dados financeiros e memórias sensíveis antes de persistir.


"""SQLite persistence layer for ZYRON interactions."""

from pathlib import Path
import sqlite3


class SQLiteRepository:
    """Encapsulates SQLite schema creation and simple persistence operations."""

    def __init__(self, database_path: Path) -> None:
        """Store the SQLite database path."""
        self.database_path = database_path

    def initialize(self) -> None:
        """Create the database directory and initial interactions table."""
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

    def save_interaction(self, user_text: str, assistant_text: str) -> None:
        """Persist one user command and assistant response."""
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "INSERT INTO interactions (user_text, assistant_text) VALUES (?, ?)",
                (user_text, assistant_text),
            )
