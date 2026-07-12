from __future__ import annotations
from src.ai.application.memory import MemoryService
from domain.models import AssistantResponse, CommandIntent, PluginMetadata, Skill
from domain.ports import PluginInterface

class MemoryPlugin(PluginInterface):
    metadata = PluginMetadata("memory", "Memória persistente", capabilities=("memory",), dependencies=("memory_service",))
    def __init__(self, memory_service: MemoryService) -> None: self._memory = memory_service
    def skills(self) -> tuple[Skill, ...]:
        return (Skill("memory", "lembrar consultar listar esquecer", ("lembre que", "lembrar", "consultar memória", "listar memórias", "esquecer"), ("lembre", "lembrar", "consultar", "listar", "esquecer", "memória"), synonyms=("meu nome é", "eu estudo")),)
    def can_handle(self, intent: CommandIntent) -> bool: return intent.skill_name == "memory"
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        text = intent.raw_text.strip(); low = text.lower()
        if low.startswith(("lembrar", "lembre", "meu nome", "eu estudo")):
            payload = text.split(" ", 1)[1] if low.startswith("lembrar ") else text
            key, _ = await self._memory.remember(payload)
            return AssistantResponse(f"Memória salva: {key}.")
        if low.startswith("consultar"):
            key = (intent.target or text.split(" ", 1)[-1]).strip(); item = await self._memory.recall(key)
            return AssistantResponse(item.value if item else "Não encontrei essa memória.")
        if low.startswith("esquecer"):
            key = (intent.target or text.split(" ", 1)[-1]).strip(); return AssistantResponse("Memória removida." if await self._memory.forget(key) else "Não encontrei essa memória.")
        items = await self._memory.list_memories(); return AssistantResponse("; ".join(f"{i.key}: {i.value}" for i in items) or "Nenhuma memória salva.")
def create_plugin(memory_service: MemoryService) -> PluginInterface: return MemoryPlugin(memory_service)
