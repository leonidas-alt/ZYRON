"""
ROADMAP DO MÓDULO

Versão Atual:

* Expõe componentes centrais da aplicação.

Próxima Versão:

* Organizar lifecycle, eventos e contratos compartilhados.

Versão Futura:

* Kernel modular multiusuário e extensível.

Dependências Futuras:

* Event bus, Dashboard Web, AWS
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


"""Core application package for configuration, orchestration and shared models."""
