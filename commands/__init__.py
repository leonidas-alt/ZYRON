"""
ROADMAP DO MÓDULO

Versão Atual:

* Expõe interpretação e roteamento de comandos.

Próxima Versão:

* Registrar handlers e aliases de forma declarativa.

Versão Futura:

* Sistema de plugins de comando por domínio.

Dependências Futuras:

* Plugin manager, SQLite, Ollama
"""

# TODO:
# Definir explicitamente exports públicos (__all__) quando o pacote ganhar mais módulos.
# FIXME:
# O pacote ainda não possui factories ou contratos formais para descoberta dinâmica.
# IMPROVEMENT:
# Documentar convenções internas para novos módulos e integrações.
# FUTURE:
# Preparar suporte a sistema de plugins, multiusuário, dashboard web, PostgreSQL, ChromaDB, Docker, Kubernetes e AWS conforme necessário.
# OPTIMIZATION:
# Evitar imports pesados no __init__ para manter inicialização rápida.
# SECURITY:
# Não expor objetos sensíveis ou clientes autenticados diretamente pelo pacote.


"""Command interpretation and routing package."""
