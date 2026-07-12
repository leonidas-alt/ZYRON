from __future__ import annotations
import asyncio, re, webbrowser
from urllib.parse import quote_plus, urlparse
from core.ports import BrowserGateway

class BrowserController(BrowserGateway):
    SITES = {"youtube":"https://www.youtube.com", "github":"https://github.com", "linkedin":"https://www.linkedin.com", "python":"https://docs.python.org/pt-br/3/", "fastapi":"https://fastapi.tiangolo.com/"}
    def normalize_url(self, site: str) -> str:
        value = site.strip()
        key = value.lower().replace("documentação", "").replace("docs", "").strip()
        if key in self.SITES: return self.SITES[key]
        if not re.match(r"^https?://", value): value = f"https://{value}"
        parsed = urlparse(value)
        return value if parsed.netloc else f"https://www.google.com/search?q={quote_plus(site)}"
    async def open_site(self, site: str) -> None:
        await asyncio.to_thread(webbrowser.open, self.normalize_url(site))
    async def google_search(self, query: str) -> None:
        await asyncio.to_thread(webbrowser.open, f"https://www.google.com/search?q={quote_plus(query)}")
    async def youtube_search(self, query: str) -> None:
        await asyncio.to_thread(webbrowser.open, f"https://www.youtube.com/results?search_query={quote_plus(query)}")
