"""
ROADMAP DO MÓDULO

Versão Atual:

* Define modelos de domínio para intents e respostas.

Próxima Versão:

* Adicionar schemas para entidades de memória, permissões e integrações.

Versão Futura:

* Contratos versionados para plugins, multiusuário e eventos assíncronos.

Dependências Futuras:

* Pydantic, OpenAPI, event bus
"""

# TODO:
# Adicionar modelos para permissões, eventos, plugins, memórias, aliases, agenda, e-mail, música e finanças.
# FIXME:
# CommandIntent ainda é genérico e pode ficar ambíguo quando comandos compostos forem adicionados.
# IMPROVEMENT:
# Considerar Pydantic para validação, serialização e contratos explícitos entre módulos.
# FUTURE:
# Criar schemas versionados para multiusuário, banco vetorial, dashboard web e integrações externas.
# OPTIMIZATION:
# Manter modelos pequenos e imutáveis para facilitar cache, comparação e testes.
# SECURITY:
# Classificar intents por nível de risco antes de rotear ações sensíveis.


"""Shared domain models used across ZYRON modules."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CommandType(str, Enum):
    """Supported high-level command categories."""

    OPEN_APP = "open_app"
    OPEN_SITE = "open_site"
    GOOGLE_SEARCH = "google_search"
    CURRENT_TIME = "current_time"
    CURRENT_WEATHER = "current_weather"
    AI_CHAT = "ai_chat"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CommandIntent:
    """Interpreted command intent produced from user speech."""

    command_type: CommandType
    raw_text: str
    target: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssistantResponse:
    """Textual response plus optional execution metadata."""

    text: str
    spoken: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
