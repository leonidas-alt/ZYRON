"""
ROADMAP DO MÓDULO

Versão Atual:

* Expõe o pacote de automação desktop e browser.

Próxima Versão:

* Centralizar adaptadores e permissões por tipo de ação.

Versão Futura:

* Plugins de automação e integração IoT.

Dependências Futuras:

* Windows APIs, IoT, Plugin manager
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


"""Desktop and browser automation package."""
