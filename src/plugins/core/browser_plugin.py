from __future__ import annotations
from automation.browser_controller import BrowserController
from domain.models import AssistantResponse, CommandIntent, PluginMetadata, Skill
from domain.ports import PluginInterface

class BrowserPlugin(PluginInterface):
    metadata=PluginMetadata("browser", "Navegação web local", capabilities=("browser",), dependencies=("browser_controller",))
    def __init__(self, browser_controller: BrowserController) -> None: self._browser = browser_controller
    def skills(self): return (Skill("browser", "abrir sites e pesquisar", ("abrir youtube", "abrir github", "abrir linkedin", "pesquisar no google", "pesquisar no youtube", "documentação python", "documentação fastapi"), ("site", "pesquisar", "google", "youtube", "github", "linkedin", "navegador", "documentação")),)
    def can_handle(self, intent: CommandIntent) -> bool: return intent.skill_name == "browser"
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        text = intent.raw_text.lower(); target = intent.target or intent.metadata.get("active_subject") or ""
        if "youtube" in text and "pesquis" in text:
            query = str(target).replace("no youtube", "").strip(); await self._browser.youtube_search(query); return AssistantResponse(f"Pesquisando no YouTube: {query}.")
        if "google" in text or "pesquis" in text or "bus" in text:
            query = str(target).replace("no google", "").strip(); await self._browser.google_search(query); return AssistantResponse(f"Pesquisando no Google: {query}.")
        site = "youtube" if "youtube" in text else "github" if "github" in text else "linkedin" if "linkedin" in text else "python" if "python" in text else "fastapi" if "fastapi" in text else str(target or intent.raw_text)
        await self._browser.open_site(site); return AssistantResponse(f"Abrindo no navegador: {site}.")
def create_plugin(browser_controller: BrowserController) -> PluginInterface: return BrowserPlugin(browser_controller)
