from __future__ import annotations
from application.memory import MemoryService
from domain.models import AssistantResponse, CommandIntent, PluginMetadata, Skill
from domain.ports import PluginInterface
from infrastructure.persistence import SQLiteRepository

class MemoryPlugin(PluginInterface):
    metadata = PluginMetadata("memory", "Memória persistente SQLite")
    def __init__(self) -> None: self._memory = MemoryService(SQLiteRepository())
    def skills(self) -> tuple[Skill, ...]:
        return (Skill("memory", "lembrar consultar listar esquecer", ("lembrar", "consultar", "listar", "esquecer"), ("lembrar", "consultar", "listar", "esquecer", "memória")),)
    def can_handle(self, intent: CommandIntent) -> bool: return intent.skill_name == "memory"
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        text = intent.raw_text.lower().strip()
        if text.startswith("lembrar") or text.startswith("lembre"):
            payload = intent.raw_text.split(" ", 1)[1] if " " in intent.raw_text else ""
            key, _, value = payload.partition("=")
            if not value: key, value = "nota", payload
            await self._memory.remember(key.strip(), value.strip())
            return AssistantResponse(f"Memória salva: {key.strip()}.")
        if text.startswith("consultar"):
            key = intent.target or intent.raw_text.split(" ", 1)[-1]
            item = await self._memory.recall(key.strip())
            return AssistantResponse(item.value if item else "Não encontrei essa memória.")
        if text.startswith("esquecer"):
            key = intent.target or intent.raw_text.split(" ", 1)[-1]
            return AssistantResponse("Memória removida." if await self._memory.forget(key.strip()) else "Não encontrei essa memória.")
        items = await self._memory.list_memories()
        return AssistantResponse("; ".join(f"{i.key}: {i.value}" for i in items) or "Nenhuma memória salva.")
def create_plugin() -> PluginInterface: return MemoryPlugin()
