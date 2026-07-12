from __future__ import annotations
import asyncio
from src.ai.application.context import ContextService
from src.ai.application.events import EventBus
from src.ai.application.memory import MemoryService
from src.ai.application.processor import CommandProcessor
from src.ai.application.router import CommandRouter
from src.ai.application.skills import IntentMatcher, SkillMatcher, SkillRegistry
from infrastructure.persistence import SQLiteRepository
from plugins.loader import PluginLoader


def test_plugins_are_discovered_automatically() -> None:
    registry = PluginLoader().discover()
    names = {plugin.metadata.name for plugin in registry.all()}
    assert {"memory", "browser", "system", "spotify", "github", "files", "cpu"}.issubset(names)


def test_skill_matcher_scores_similar_commands() -> None:
    registry = PluginLoader().discover()
    skill_registry = SkillRegistry()
    for skill in registry.skills():
        skill_registry.register(skill)
    intent = IntentMatcher(SkillMatcher(skill_registry)).match("abra spotify")
    assert intent.skill_name in {"application", "spotify"}
    assert intent.confidence >= 0.5


def test_memory_repository_persists_memories(tmp_path) -> None:
    repo = SQLiteRepository(str(tmp_path / "zyron.db"))
    service = MemoryService(repo)
    asyncio.run(service.remember("cor", "azul"))
    item = asyncio.run(service.recall("cor"))
    assert item is not None
    assert item.value == "azul"


def test_command_processor_pipeline_saves_history(tmp_path) -> None:
    repo = SQLiteRepository(str(tmp_path / "zyron.db"))
    registry = PluginLoader().discover()
    skill_registry = SkillRegistry()
    for skill in registry.skills():
        skill_registry.register(skill)
    processor = CommandProcessor(
        IntentMatcher(SkillMatcher(skill_registry)),
        CommandRouter(registry),
        ContextService(),
        MemoryService(repo),
        EventBus(),
    )
    response = asyncio.run(processor.process("lembrar projeto=ZYRON"))
    history = asyncio.run(repo.get_recent_interactions())
    assert "Memória salva" in response
    assert history[-1].user_text == "lembrar projeto=ZYRON"
