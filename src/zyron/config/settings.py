from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    assistant_name: str
    owner_name: str
    language: str
    mode: str
    ollama_base_url: str
    ollama_model: str
    ollama_timeout_seconds: float
    database_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        return cls(
            assistant_name=os.getenv("ZYRON_ASSISTANT_NAME", "ZYRON"),
            owner_name=os.getenv("ZYRON_OWNER_NAME", "Leonidas"),
            language=os.getenv("ZYRON_LANGUAGE", "pt-BR"),
            mode=os.getenv("ZYRON_MODE", "text").strip().lower(),
            ollama_base_url=os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434",
            ).rstrip("/"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            ollama_timeout_seconds=float(
                os.getenv("OLLAMA_TIMEOUT_SECONDS", "60")
            ),
            database_path=Path(
                os.getenv("ZYRON_DATABASE_PATH", "data/zyron.db")
            ),
        )