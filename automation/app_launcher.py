"""
ROADMAP DO MÓDULO

Versão Atual:

* Abre aplicativos por comando shell.

Próxima Versão:

* Adicionar catálogo seguro de apps, aliases e validação de caminhos.

Versão Futura:

* Automação contextual, perfis por ambiente e integração com launcher Windows.

Dependências Futuras:

* SQLite/PostgreSQL, Windows Registry, PowerShell
"""

# TODO:
# Criar catálogo de aplicativos e testes para aliases como VSCode, Spotify, Chrome, Steam e Discord.
# FIXME:
# subprocess.Popen com shell=True é frágil e pode executar entradas indesejadas se o comando vier direto do usuário.
# IMPROVEMENT:
# Usar allowlist de comandos, caminhos absolutos, Windows Registry e validação de argumentos.
# FUTURE:
# Adicionar perfis de automação, rotinas de trabalho/jogo e integração com painel administrativo.
# OPTIMIZATION:
# Cachear resolução de caminhos de aplicativos para evitar buscas repetidas.
# SECURITY:
# Bloquear comandos arbitrários e registrar auditoria para toda automação local executada.


"""Windows application launcher abstraction."""

import subprocess


class AppLauncher:
    """Opens installed desktop applications by command or executable name."""

    def open_application(self, app_name: str) -> None:
        """Launch an application without blocking the assistant loop."""
        subprocess.Popen(app_name, shell=True)  # noqa: S602 - intended desktop automation hook
