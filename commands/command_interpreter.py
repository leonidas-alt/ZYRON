"""
ROADMAP DO MÓDULO

Versão Atual:

* Converte texto em intents usando regras simples.

Próxima Versão:

* Adicionar aliases, normalização e classificação por IA em JSON.

Versão Futura:

* Planner multi-etapas, plugins de comandos e aprendizado com correções.

Dependências Futuras:

* Ollama, SQLite aliases, sistema de plugins
"""

# TODO:
# Cobrir todos os tipos de comando com testes parametrizados e exemplos reais em português.
# FIXME:
# A interpretação atual depende de prefixos rígidos e falha com linguagem natural variada.
# IMPROVEMENT:
# Adicionar aliases persistidos em SQLite e classificação por Ollama com saída JSON validada.
# FUTURE:
# Suportar planner multi-etapas, sistema de plugins, comandos de Spotify, Calendar, Gmail, IoT e financeiro.
# OPTIMIZATION:
# Pré-compilar padrões e normalizar texto uma única vez por comando.
# SECURITY:
# Marcar intents potencialmente perigosas para confirmação antes de executar automações ou operações financeiras.


"""Rule-based command interpreter for the MVP."""

from core.models import CommandIntent, CommandType


class CommandInterpreter:
    """Transforms transcribed text into structured command intents."""

    def interpret(self, text: str) -> CommandIntent:
        """Classify the command using simple Portuguese keyword rules."""
        normalized = text.lower().strip()
        if normalized.startswith("abrir aplicativo "):
            return CommandIntent(CommandType.OPEN_APP, text, normalized.replace("abrir aplicativo ", "", 1))
        if normalized.startswith("abrir site "):
            return CommandIntent(CommandType.OPEN_SITE, text, normalized.replace("abrir site ", "", 1))
        if normalized.startswith("pesquisar ") or normalized.startswith("pesquise "):
            query = normalized.replace("pesquisar ", "", 1).replace("pesquise ", "", 1)
            return CommandIntent(CommandType.GOOGLE_SEARCH, text, query)
        if "horas" in normalized or "horário" in normalized:
            return CommandIntent(CommandType.CURRENT_TIME, text)
        if "temperatura" in normalized or "clima" in normalized:
            return CommandIntent(CommandType.CURRENT_WEATHER, text)
        if normalized:
            return CommandIntent(CommandType.AI_CHAT, text)
        return CommandIntent(CommandType.UNKNOWN, text)
