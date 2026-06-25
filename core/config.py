"""
ROADMAP DO MÓDULO

Versão Atual:

* Carrega Settings por variáveis de ambiente e .env.

Próxima Versão:

* Validar configurações obrigatórias e separar secrets de preferências.

Versão Futura:

* Gerenciar perfis, cofres de segredo e configuração remota segura.

Dependências Futuras:

* Vault local, AWS Secrets Manager, Docker secrets
"""

# TODO:
# Validar configurações obrigatórias por funcionalidade e emitir mensagens claras quando variáveis estiverem ausentes.
# FIXME:
# Configurações sensíveis e preferências não sensíveis ainda estão misturadas no mesmo objeto.
# IMPROVEMENT:
# Separar Settings em grupos como AISettings, VoiceSettings, WeatherSettings, DatabaseSettings e SecuritySettings.
# FUTURE:
# Suportar perfis multiusuário, configuração via painel web, Docker secrets, AWS Secrets Manager e cofre local.
# OPTIMIZATION:
# Evitar leituras repetidas de ambiente mantendo configurações imutáveis e cacheadas no início do processo.
# SECURITY:
# Nunca persistir chaves em logs; validar permissões de arquivos .env e tokens OAuth futuros.


"""Configuration loading for ZYRON."""

from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import os


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings loaded from environment variables."""

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
        """Load settings from a .env file and process environment variables."""
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
