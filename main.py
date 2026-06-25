"""
ROADMAP DO MÓDULO

Versão Atual:

* Inicializa configurações e executa o ciclo principal do assistente.

Próxima Versão:

* Adicionar modo serviço/tray e flags de linha de comando.

Versão Futura:

* Suportar múltiplos perfis de execução, Docker e orquestração em nuvem.

Dependências Futuras:

* Windows Service, Docker, Kubernetes, AWS
"""

# TODO:
# Adicionar argumentos de linha de comando para modo debug, modo silencioso e execução única.
# FIXME:
# O processo principal ainda não possui tratamento de encerramento gracioso por sinal do sistema.
# IMPROVEMENT:
# Separar bootstrap de runtime para permitir testes de inicialização sem entrar no loop infinito.
# FUTURE:
# Suportar execução como Windows Service, tray app, Docker container de desenvolvimento e worker remoto em AWS.
# OPTIMIZATION:
# Inicializar componentes pesados sob demanda para reduzir tempo de startup.
# SECURITY:
# Validar perfil de execução antes de permitir comandos locais com impacto no sistema operacional.


"""Application entrypoint for the ZYRON local assistant."""

from core.application import ZyronApplication
from core.config import Settings


def main() -> None:
    """Create and run the ZYRON application."""
    settings = Settings.from_env()
    app = ZyronApplication(settings=settings)
    app.run()


if __name__ == "__main__":
    main()
