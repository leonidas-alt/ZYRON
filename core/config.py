from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import os

@dataclass(frozen=True)
class Settings:

    assistant_name: str = "Zyron"
    owner_name: str = "Leonidas"
    language: str = "pt-BR"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    whisper_model: str = "small"
    edge_tts_voice: str = "pt-BR-AntonioNeural"
    openweather_api_key: str = ""
    openweather_city: str = "Sao Paulo"
    database_path: Path = Path("data/zyron.db")
    wake_word: str = "zyron"

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            assistant_name=os.getenv("ZYRON_ASSISTANT_NAME", cls.assistant_name),
            owner_name=os.getenv("ZYRON_OWNER_NAME", cls.owner_name),
            language=os.getenv("ZYRON_LANGUAGE", cls.language),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", cls.ollama_base_url),
            ollama_model=os.getenv("OLLAMA_MODEL", cls.ollama_model),
            whisper_model=os.getenv("WHISPER_MODEL", cls.whisper_model),
            edge_tts_voice=os.getenv("EDGE_TTS_VOICE", cls.edge_tts_voice),
            openweather_api_key=os.getenv("OPENWEATHER_API_KEY", cls.openweather_api_key),
            openweather_city=os.getenv("OPENWEATHER_CITY", cls.openweather_city),
            database_path=Path(os.getenv("ZYRON_DATABASE_PATH", str(cls.database_path))),
            wake_word=os.getenv("ZYRON_WAKE_WORD", cls.wake_word).lower(),
        )
