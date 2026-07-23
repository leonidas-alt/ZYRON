from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    assistant_name: str
    owner_name: str

    mode: str

    ollama_base_url: str
    ollama_model: str
    ollama_timeout_seconds: int

    database_path: str

    audio_sample_rate: int
    audio_channels: int
    audio_dtype: str
    audio_device: int | str | None

    whisper_model: str
    whisper_device: str
    whisper_compute_type: str
    whisper_language: str | None
    whisper_beam_size: int
    whisper_vad_filter: bool

    voice_name: str
    voice_rate: int
    voice_volume: int

    wake_words: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            assistant_name=_get_string(
                "ZYRON_ASSISTANT_NAME",
                "Zyron",
            ),
            owner_name=_get_string(
                "ZYRON_OWNER_NAME",
                "Usuário",
            ),
            mode=_get_string(
                "ZYRON_MODE",
                "text",
            ),
            ollama_base_url=_get_string(
                "ZYRON_OLLAMA_BASE_URL",
                "http://localhost:11434",
            ),
            ollama_model=_get_string(
                "ZYRON_OLLAMA_MODEL",
                "llama3.2",
            ),
            ollama_timeout_seconds=_get_int(
                "ZYRON_OLLAMA_TIMEOUT_SECONDS",
                120,
            ),
            database_path=_get_string(
                "ZYRON_DATABASE_PATH",
                "data/zyron.db",
            ),
            audio_sample_rate=_get_int(
                "ZYRON_AUDIO_SAMPLE_RATE",
                16000,
            ),
            audio_channels=_get_int(
                "ZYRON_AUDIO_CHANNELS",
                1,
            ),
            audio_dtype=_get_string(
                "ZYRON_AUDIO_DTYPE",
                "int16",
            ),
            audio_device=_get_optional_string(
                "ZYRON_AUDIO_DEVICE",
            ),
            whisper_model=_get_string(
                "ZYRON_WHISPER_MODEL",
                "small",
            ),
            whisper_device=_get_string(
                "ZYRON_WHISPER_DEVICE",
                "cpu",
            ),
            whisper_compute_type=_get_string(
                "ZYRON_WHISPER_COMPUTE_TYPE",
                "int8",
            ),
            whisper_language=_get_optional_string(
                "ZYRON_WHISPER_LANGUAGE",
            ),
            whisper_beam_size=_get_int(
                "ZYRON_WHISPER_BEAM_SIZE",
                5,
            ),
            whisper_vad_filter=_get_bool(
                "ZYRON_WHISPER_VAD_FILTER",
                True,
            ),
            voice_name=_get_string(
                "ZYRON_VOICE_NAME",
                "pt-BR-FranciscaNeural",
            ),
            voice_rate=_get_int(
                "ZYRON_VOICE_RATE",
                0,
            ),
            voice_volume=_get_int(
                "ZYRON_VOICE_VOLUME",
                100,
            ),
            wake_words=_get_tuple(
                "ZYRON_WAKE_WORDS",
                ("zyron",),
            ),
        )


def _get_string(
    key: str,
    default: str,
) -> str:
    value = os.getenv(
        key,
        default,
    ).strip()

    return value or default


def _get_optional_string(
    key: str,
) -> str | None:
    value = os.getenv(key)

    if value is None:
        return None

    value = value.strip()

    return value or None


def _get_int(
    key: str,
    default: int,
) -> int:
    value = os.getenv(key)

    if value is None:
        return default

    return int(value)


def _get_bool(
    key: str,
    default: bool,
) -> bool:
    value = os.getenv(key)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _get_tuple(
    key: str,
    default: tuple[str, ...],
) -> tuple[str, ...]:
    value = os.getenv(key)

    if value is None:
        return default

    items = tuple(
        item.strip()
        for item in value.split(",")
        if item.strip()
    )

    return items or default
