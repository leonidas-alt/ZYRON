from urllib.parse import quote_plus
import webbrowser

class BrowserController:

    def open_site(self, site: str) -> None:
        url = site if site.startswith(("http://", "https://")) else f"https://{site}"
        webbrowser.open(url)

    def google_search(self, query: str) -> None:
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
