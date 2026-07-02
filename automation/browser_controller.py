from urllib.parse import quote_plus
import webbrowser

class BrowserController:

    def open_site(self, site: str) -> None:
        """Open a site, adding https:// when no scheme is provided."""
        url = site if site.startswith(("http://", "https://")) else f"https://{site}"
        webbrowser.open(url)

    def google_search(self, query: str) -> None:
        """Open Google search results for a query."""
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
