from __future__ import annotations
from src.ai.application.processor import IntentRouter
from bootstrap.container import ApplicationContainer, build_base_container, build_text_container, build_voice_container
from core.config import Settings
from domain.ports import InteractionRepository

class ZyronApplication:
    def __init__(self, settings: Settings, repository: InteractionRepository | None = None, speech_to_text: object | None = None, text_to_speech: object | None = None, wake_word_detector: object | None = None, interpreter: object | None = None, router: IntentRouter | None = None, plugin_manager: object | None = None, memory: object | None = None) -> None:
        self.container = build_base_container(settings, repository=repository, router=router)
        self.settings = settings; self.repository = self.container.repository; self.processor = self.container.command_processor
    async def process_text(self, command_text: str) -> str:
        self.processor._context.context.recent = await self.repository.get_recent_interactions(5)
        return await self.processor.process(command_text)
