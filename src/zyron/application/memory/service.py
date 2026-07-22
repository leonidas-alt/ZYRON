from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any, Protocol


logger = logging.getLogger(__name__)


class MemoryRepositoryProtocol(Protocol):

    def save_memory(
        self,
        key: str,
        value: str,
    ) -> None:

        ...

    def get_memory(
        self,
        key: str,
    ) -> dict[str, Any] | None:

        ...

    def delete_memory(
        self,
        key: str,
    ) -> bool:
      
        ...

    def list_memories(
        self,
    ) -> list[dict[str, Any]]:
      
        ...

    def save_interaction(
        self,
        user_text: str,
        assistant_text: str,
        source: str,
    ) -> None:
      
        ...


class MemoryService:

    MAX_KEY_LENGTH = 150
    MAX_VALUE_LENGTH = 5_000
    MAX_INTERACTION_LENGTH = 20_000

    def __init__(
        self,
        repository: MemoryRepositoryProtocol,
    ) -> None:

        self._repository = repository

    def remember(
        self,
        key: str,
        value: str,
    ) -> None:

        normalized_key = self._normalize_key(key)
        cleaned_value = self._clean_value(value)

        self._validate_key(normalized_key)
        self._validate_value(cleaned_value)

        self._repository.save_memory(
            key=normalized_key,
            value=cleaned_value,
        )

        logger.info(
            "Memória salva ou atualizada: key=%s",
            normalized_key,
        )

    def recall(
        self,
        key: str,
    ) -> str | None:

        normalized_key = self._normalize_key(key)

        if not normalized_key:
            return None

        memory = self._repository.get_memory(normalized_key)

        if memory is None:
            logger.debug(
                "Memória não encontrada: key=%s",
                normalized_key,
            )

            return None

        value = memory.get("value")

        if value is None:
            return None

        return str(value)

    def forget(
        self,
        key: str,
    ) -> bool:

        normalized_key = self._normalize_key(key)

        if not normalized_key:
            return False

        deleted = self._repository.delete_memory(normalized_key)

        if deleted:
            logger.info(
                "Memória removida: key=%s",
                normalized_key,
            )
        else:
            logger.debug(
                "Tentativa de remover memória inexistente: key=%s",
                normalized_key,
            )

        return deleted

    def list_all(
        self,
    ) -> list[dict[str, str]]:

        memories = self._repository.list_memories()

        formatted_memories: list[dict[str, str]] = []

        for memory in memories:
            formatted_memories.append(
                {
                    "key": str(memory.get("key", "")),
                    "value": str(memory.get("value", "")),
                    "created_at": str(
                        memory.get("created_at", "")
                    ),
                    "updated_at": str(
                        memory.get("updated_at", "")
                    ),
                }
            )

        return formatted_memories

    def exists(
        self,
        key: str,
    ) -> bool:

        return self.recall(key) is not None

    def update(
        self,
        key: str,
        value: str,
    ) -> bool:

        normalized_key = self._normalize_key(key)

        if self.recall(normalized_key) is None:
            return False

        self.remember(
            key=normalized_key,
            value=value,
        )

        return True

    def get_or_default(
        self,
        key: str,
        default: str = "",
    ) -> str:

        value = self.recall(key)

        if value is None:
            return default

        return value

    def save_interaction(
        self,
        user_text: str,
        assistant_text: str,
        source: str = "unknown",
    ) -> None:

        cleaned_user_text = self._clean_text(user_text)
        cleaned_assistant_text = self._clean_text(assistant_text)
        cleaned_source = self._clean_source(source)

        if not cleaned_user_text:
            return

        if not cleaned_assistant_text:
            return

        self._validate_interaction_text(
            text=cleaned_user_text,
            field_name="user_text",
        )

        self._validate_interaction_text(
            text=cleaned_assistant_text,
            field_name="assistant_text",
        )

        self._repository.save_interaction(
            user_text=cleaned_user_text,
            assistant_text=cleaned_assistant_text,
            source=cleaned_source,
        )

        logger.debug(
            "Interação salva: source=%s",
            cleaned_source,
        )

    @classmethod
    def _normalize_key(
        cls,
        key: str,
    ) -> str:

        if not isinstance(key, str):
            return ""

        normalized = unicodedata.normalize(
            "NFKC",
            key,
        )

        normalized = normalized.strip().lower()

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        normalized = normalized.rstrip("?.!,")

        prefixes = (
            "o meu ",
            "a minha ",
            "meu ",
            "minha ",
            "o ",
            "a ",
        )

        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
                break

        return normalized

    @staticmethod
    def _clean_value(
        value: str,
    ) -> str:

        if not isinstance(value, str):
            return ""

        return " ".join(value.strip().split())

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:

        if not isinstance(text, str):
            return ""

        return text.strip()

    @staticmethod
    def _clean_source(
        source: str,
    ) -> str:

        if not isinstance(source, str):
            return "unknown"

        cleaned = source.strip().lower()

        cleaned = re.sub(
            r"[^a-z0-9_-]",
            "_",
            cleaned,
        )

        return cleaned or "unknown"

    @classmethod
    def _validate_key(
        cls,
        key: str,
    ) -> None:

        if not key:
            raise ValueError(
                "A chave da memória não pode estar vazia."
            )

        if len(key) > cls.MAX_KEY_LENGTH:
            raise ValueError(
                "A chave da memória ultrapassa o limite de "
                f"{cls.MAX_KEY_LENGTH} caracteres."
            )

    @classmethod
    def _validate_value(
        cls,
        value: str,
    ) -> None:

        if not value:
            raise ValueError(
                "O valor da memória não pode estar vazio."
            )

        if len(value) > cls.MAX_VALUE_LENGTH:
            raise ValueError(
                "O valor da memória ultrapassa o limite de "
                f"{cls.MAX_VALUE_LENGTH} caracteres."
            )

    @classmethod
    def _validate_interaction_text(
        cls,
        text: str,
        field_name: str,
    ) -> None:

        if len(text) > cls.MAX_INTERACTION_LENGTH:
            raise ValueError(
                f"O campo '{field_name}' ultrapassa o limite de "
                f"{cls.MAX_INTERACTION_LENGTH} caracteres."
            )
