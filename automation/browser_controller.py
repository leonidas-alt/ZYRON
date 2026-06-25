"""
ROADMAP DO MÓDULO

Versão Atual:

* Abre sites e pesquisas no navegador padrão.

Próxima Versão:

* Validar URLs, favoritos e provedores de busca configuráveis.

Versão Futura:

* Automação web avançada, dashboard e navegação assistida por IA.

Dependências Futuras:

* Playwright, Dashboard Web, policy engine
"""

# TODO:
# Criar testes para normalização de URL, pesquisa Google e provedores de busca configuráveis.
# FIXME:
# URLs ainda não são validadas contra esquemas perigosos ou domínios bloqueados.
# IMPROVEMENT:
# Adicionar favoritos, aliases de sites e seleção de navegador por perfil.
# FUTURE:
# Integrar Playwright para automação web avançada e dashboard local de navegação assistida.
# OPTIMIZATION:
# Reutilizar abas/janelas quando possível e evitar abrir buscas duplicadas.
# SECURITY:
# Validar esquemas permitidos e adicionar confirmação para sites sensíveis ou downloads.


"""Browser automation helpers for sites and Google searches."""

from urllib.parse import quote_plus
import webbrowser


class BrowserController:
    """Opens URLs and search pages in the default browser."""

    def open_site(self, site: str) -> None:
        """Open a site, adding https:// when no scheme is provided."""
        url = site if site.startswith(("http://", "https://")) else f"https://{site}"
        webbrowser.open(url)

    def google_search(self, query: str) -> None:
        """Open Google search results for a query."""
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
