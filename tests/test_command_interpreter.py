"""
ROADMAP DO MÓDULO

Versão Atual:

* Valida interpretação básica de comando de pesquisa.

Próxima Versão:

* Cobrir todos os intents, edge cases e roteamento com mocks.

Versão Futura:

* Testes de integração com áudio, banco, Ollama fake e automação simulada.

Dependências Futuras:

* pytest, respx/requests-mock, fixtures de áudio
"""

# TODO:
# Adicionar testes para abrir app, abrir site, horário, clima, chat, unknown e entradas vazias.
# FIXME:
# A suíte ainda não valida roteador, banco, serviços externos, voz ou automação.
# IMPROVEMENT:
# Usar parametrização, fixtures e mocks para cobrir fluxos sem depender de rede ou sistema operacional.
# FUTURE:
# Adicionar testes de integração com Ollama fake, áudio de exemplo, SQLite temporário e comandos por plugin.
# OPTIMIZATION:
# Manter testes rápidos separando unitários de integração lenta.
# SECURITY:
# Incluir testes para bloqueio de comandos perigosos, URLs inválidas e vazamento de secrets.


"""Tests for command interpretation."""

from commands.command_interpreter import CommandInterpreter
from core.models import CommandType


def test_interprets_google_search() -> None:
    """Ensure Portuguese search commands map to Google search intents."""
    intent = CommandInterpreter().interpret("pesquisar python 3.12")
    assert intent.command_type == CommandType.GOOGLE_SEARCH
    assert intent.target == "python 3.12"
