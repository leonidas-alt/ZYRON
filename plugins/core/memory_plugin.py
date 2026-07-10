from __future__ import annotations

from application.memory import MemoryService
from domain.models import AssistantResponse, CommandIntent, PluginMetadata, Skill
from domain.ports import PluginInterface
from infrastructure.persistence import SQLiteRepository
from plugins.dependencies import PluginDependencies


class MemoryPlugin(PluginInterface):
    """Plugin that exposes persistent memory commands."""

    metadata = PluginMetadata("memory", "Memória persistente SQLite")

    def __init__(self, memory: MemoryService) -> None:
        self._memory = memory

    def skills(self) -> tuple[Skill, ...]:
        return (
            Skill(
                name="memory",
                description="lembrar consultar listar esquecer",
                examples=("lembrar", "consultar", "listar", "esquecer"),
                keywords=("lembrar", "consultar", "listar", "esquecer", "memória"),
            ),
        )

    def can_handle(self, intent: CommandIntent) -> bool:
        return intent.skill_name == "memory"

    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        text = intent.raw_text.lower().strip()
        if text.startswith(("lembrar", "lembre")):
            return await self._remember(intent.raw_text)
        if text.startswith("consultar"):
            return await self._recall(self._argument(intent))
        if text.startswith("esquecer"):
            return await self._forget(self._argument(intent))
        return await self._list()

    async def _remember(self, raw_text: str) -> AssistantResponse:
        payload = raw_text.split(" ", 1)[1] if " " in raw_text else ""
        key, separator, value = payload.partition("=")
        if not separator:
            key, value = "nota", payload
        key = key.strip()
        await self._memory.remember(key, value.strip())
        return AssistantResponse(f"Memória salva: {key}.")

    async def _recall(self, key: str) -> AssistantResponse:
        item = await self._memory.recall(key)
        return AssistantResponse(item.value if item else "Não encontrei essa memória.")

    async def _forget(self, key: str) -> AssistantResponse:
        removed = await self._memory.forget(key)
        return AssistantResponse("Memória removida." if removed else "Não encontrei essa memória.")

    async def _list(self) -> AssistantResponse:
        items = await self._memory.list_memories()
        text = "; ".join(f"{item.key}: {item.value}" for item in items)
        return AssistantResponse(text or "Nenhuma memória salva.")

    def _argument(self, intent: CommandIntent) -> str:
        return (intent.target or intent.raw_text.split(" ", 1)[-1]).strip()


def create_plugin(dependencies: PluginDependencies | None = None) -> PluginInterface:
    memory = dependencies.memory if dependencies and dependencies.memory else None
    return MemoryPlugin(memory or MemoryService(SQLiteRepository()))
