from __future__ import annotations

import asyncio
from pathlib import Path

from application.context import ConversationContext
from application.memory import MemoryService
from application.skills import IntentMatcher, SkillMatcher, SkillRegistry
from automation.app_launcher import AppLauncher
from automation.browser_controller import BrowserController
from bootstrap.container import build_text_container
from core.config import Settings
from domain.models import Skill
from infrastructure.persistence import SQLiteRepository
from plugins.core.memory_plugin import MemoryPlugin
from plugins.registry import PluginRegistry


def test_context_tracks_metadata_and_resolves_references() -> None:
    ctx = ConversationContext()
    ctx.update("Abra YouTube", "Abrindo", plugin_name="browser", target="YouTube", metadata={"site": "YouTube"})
    assert ctx.resolve_reference("pesquise curso de Docker nele") == "YouTube"
    assert ctx.to_metadata()["last_site"] == "YouTube"
    ctx.clear(); assert ctx.active_subject is None
    ctx.reset(); assert ctx.interaction_count == 0


def test_memory_parser_understands_simple_natural_language(tmp_path: Path) -> None:
    service = MemoryService(SQLiteRepository(str(tmp_path / "m.db")))
    assert service.parse_memory("lembre que meu editor favorito é VSCode") == ("editor favorito", "vscode")
    assert service.parse_memory("lembre que gosto de café") == ("preferência", "gosto de café")
    assert service.parse_memory("meu nome é Leonidas") == ("nome", "leonidas")
    assert service.parse_memory("eu estudo ADS") == ("curso", "ads")


def test_skill_matcher_uses_priority_to_avoid_spotify_ambiguity() -> None:
    registry = SkillRegistry()
    registry.register(Skill("application", "apps", ("abrir spotify",), ("abrir", "spotify")))
    registry.register(Skill("browser", "browser", ("abrir site",), ("abrir", "site")))
    match = SkillMatcher(registry).match("abrir spotify")
    assert match is not None
    assert match.skill.name == "application"
    assert match.confidence >= 0.5


def test_plugin_registry_rejects_duplicate_plugins(tmp_path: Path) -> None:
    service = MemoryService(SQLiteRepository(str(tmp_path / "m.db")))
    registry = PluginRegistry()
    registry.register(MemoryPlugin(service))
    try:
        registry.register(MemoryPlugin(service))
    except ValueError as exc:
        assert "duplicado" in str(exc)
    else:
        raise AssertionError("duplicate plugin was accepted")


def test_browser_url_normalization_and_application_catalog() -> None:
    browser = BrowserController()
    assert browser.normalize_url("github") == "https://github.com"
    assert browser.normalize_url("example.com") == "https://example.com"
    launcher = AppLauncher()
    assert launcher.is_supported("VSCode")
    assert not launcher.is_supported("rm -rf /")


def test_container_wires_dependencies(tmp_path: Path) -> None:
    settings = Settings(database_path=tmp_path / "zyron.db")
    container = build_text_container(settings)
    assert container.memory_service is not None
    assert container.context_service is not None
    assert container.browser_controller is not None
    assert container.application_launcher is not None
    asyncio.run(container.initialize())
