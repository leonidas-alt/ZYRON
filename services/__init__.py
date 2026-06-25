"""
ROADMAP DO MÓDULO

Versão Atual:

* Expõe serviços externos e utilitários de domínio.

Próxima Versão:

* Padronizar clientes HTTP, retries e autenticação.

Versão Futura:

* Catálogo de integrações de produtividade e finanças.

Dependências Futuras:

* Spotify, Google APIs, OpenWeather
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


"""External and domain services package."""
