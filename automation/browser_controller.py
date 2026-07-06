from __future__ import annotations
import asyncio
from urllib.parse import quote_plus
import webbrowser
from core.ports import BrowserGateway

class BrowserController(BrowserGateway):

    async def open_site(self, site: str) -> None:
        url = site if site.startswith(("http://", "https://")) else f"https://{site}"
        await asyncio.to_thread(webbrowser.open, url)

    async def google_search(self, query: str) -> None:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        await asyncio.to_thread(webbrowser.open, url)
