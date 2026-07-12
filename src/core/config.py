from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import os


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    assistant_name: str = "ZYRON"
    owner_name: str = "Leonidas"
    language: str = "pt-BR"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    openweather_api_key: str = ""
    openweather_city: str = "Sao Paulo"
    database_path: Path = Path("data/zyron.db")

    voice_enabled: bool = True
    voice_require_wake_word: bool = False
    voice_wake_word: str = "zyron"
    microphone_device: str | None = None
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    audio_max_duration_seconds: float = 10.0
    audio_silence_duration_seconds: float = 1.5
    whisper_model: str = "small"
    whisper_language: str = "pt"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    tts_provider: str = "edge"
    tts_voice: str = "pt-BR-AntonioNeural"
    tts_rate: str = "+0%"
    tts_volume: str = "+0%"

    # Backwards-compatible aliases used by older tests/integrations.
    edge_tts_voice: str = "pt-BR-AntonioNeural"
    wake_word: str = "zyron"

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        assistant_name = os.getenv("ASSISTANT_NAME", os.getenv("ZYRON_ASSISTANT_NAME", cls.assistant_name))
        owner_name = os.getenv("OWNER_NAME", os.getenv("ZYRON_OWNER_NAME", cls.owner_name))
        voice_wake_word = os.getenv("VOICE_WAKE_WORD", os.getenv("ZYRON_WAKE_WORD", cls.voice_wake_word)).lower()
        tts_voice = os.getenv("TTS_VOICE", os.getenv("EDGE_TTS_VOICE", cls.tts_voice))
        return cls(
            assistant_name=assistant_name,
            owner_name=owner_name,
            language=os.getenv("ZYRON_LANGUAGE", cls.language),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", cls.ollama_base_url),
            ollama_model=os.getenv("OLLAMA_MODEL", cls.ollama_model),
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY", cls.openweather_api_key),
            openweather_city=os.getenv("OPENWEATHER_CITY", cls.openweather_city),
            database_path=Path(os.getenv("ZYRON_DATABASE_PATH", str(cls.database_path))),
            voice_enabled=_bool("VOICE_ENABLED", cls.voice_enabled),
            voice_require_wake_word=_bool("VOICE_REQUIRE_WAKE_WORD", cls.voice_require_wake_word),
            voice_wake_word=voice_wake_word,
            microphone_device=os.getenv("MICROPHONE_DEVICE") or None,
            audio_sample_rate=int(os.getenv("AUDIO_SAMPLE_RATE", cls.audio_sample_rate)),
            audio_channels=int(os.getenv("AUDIO_CHANNELS", cls.audio_channels)),
            audio_max_duration_seconds=float(os.getenv("AUDIO_MAX_DURATION_SECONDS", cls.audio_max_duration_seconds)),
            audio_silence_duration_seconds=float(os.getenv("AUDIO_SILENCE_DURATION_SECONDS", cls.audio_silence_duration_seconds)),
            whisper_model=os.getenv("WHISPER_MODEL", cls.whisper_model),
            whisper_language=os.getenv("WHISPER_LANGUAGE", cls.whisper_language),
            whisper_device=os.getenv("WHISPER_DEVICE", cls.whisper_device),
            whisper_compute_type=os.getenv("WHISPER_COMPUTE_TYPE", cls.whisper_compute_type),
            tts_provider=os.getenv("TTS_PROVIDER", cls.tts_provider),
            tts_voice=tts_voice,
            tts_rate=os.getenv("TTS_RATE", cls.tts_rate),
            tts_volume=os.getenv("TTS_VOLUME", cls.tts_volume),
            edge_tts_voice=tts_voice,
            wake_word=voice_wake_word,
        )
