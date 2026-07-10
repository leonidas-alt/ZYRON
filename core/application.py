from __future__ import annotations

from application.context import ContextService, ConversationContext
from application.events import EventBus
from application.memory import MemoryService
from application.processor import CommandProcessor
from application.router import CommandRouter
from application.scheduler import Scheduler
from application.skills import IntentMatcher, SkillMatcher, SkillRegistry
from core.config import Settings
from domain.models import CommandIntent
from domain.ports import InteractionRepository, SpeechRecognizer, SpeechSynthesizer, WakeWordService
from infrastructure.persistence import SQLiteRepository
from plugins.dependencies import PluginDependencies
from plugins.loader import PluginLoader
from services.time_service import TimeService
from services.weather_service import WeatherService
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from voice.wake_word import WakeWordDetector


class ZyronApplication:
    """Composition root for the ZYRON assistant."""

    def __init__(
        self,
        settings: Settings,
        repository: InteractionRepository | None = None,
        speech_to_text: SpeechRecognizer | None = None,
        text_to_speech: SpeechSynthesizer | None = None,
        wake_word_detector: WakeWordService | None = None,
        interpreter: object | None = None,
        router: object | None = None,
        plugin_manager: object | None = None,
        memory: object | None = None,
    ) -> None:
        self.settings = settings
        self.repository = repository or SQLiteRepository(str(settings.database_path))
        self.time_service = TimeService()
        self.weather_service = WeatherService(
            settings.openweather_api_key,
            settings.openweather_city,
        )
        self.speech_to_text = speech_to_text or SpeechToText(
            settings.whisper_model,
            settings.language,
        )
        self.text_to_speech = text_to_speech or TextToSpeech(settings.edge_tts_voice)
        self.wake_word_detector = wake_word_detector or WakeWordDetector(settings.wake_word)

        self.memory_service = MemoryService(self.repository)  # type: ignore[arg-type]
        self.plugin_registry = PluginLoader(
            dependencies=PluginDependencies(memory=self.memory_service),
        ).discover()
        self.context_service = ContextService(ConversationContext())
        self.intent_matcher = self._build_intent_matcher()
        self.event_bus = EventBus()
        self.scheduler = Scheduler()
        self.router = router or CommandRouter(self.plugin_registry)
        self.processor = CommandProcessor(
            self.intent_matcher,
            self.router,  # type: ignore[arg-type]
            self.context_service,
            self.memory_service,
            self.event_bus,
        )

    def _build_intent_matcher(self) -> IntentMatcher:
        skill_registry = SkillRegistry()
        for skill in self.plugin_registry.skills():
            skill_registry.register(skill)
        return IntentMatcher(SkillMatcher(skill_registry))

    async def process_text(self, command_text: str) -> str:
        recent = await self.repository.get_recent_interactions(5)
        self.context_service.load_recent(recent)
        if self._is_legacy_router():
            return await self._process_with_legacy_router(command_text)
        return await self.processor.process(command_text)

    async def _process_with_legacy_router(self, command_text: str) -> str:
        intent = self._with_context(self.intent_matcher.match(command_text))
        response = await self.router.route(intent)
        await self.repository.save_interaction(command_text, response.text)
        return response.text

    def _with_context(self, intent: CommandIntent) -> CommandIntent:
        return CommandIntent(
            command_type=intent.command_type,
            raw_text=intent.raw_text,
            target=intent.target,
            confidence=intent.confidence,
            skill_name=intent.skill_name,
            plugin_name=intent.plugin_name,
            metadata=self.context_service.enrich(intent.metadata),
        )

    def _is_legacy_router(self) -> bool:
        return not isinstance(self.router, CommandRouter)

    async def bootstrap(self) -> None:
        await self.repository.initialize()
        await self.scheduler.start()
        current_time = self.time_service.current_time_text()
        temperature = await self.weather_service.current_temperature_text()
        greeting = (
            f"{self.settings.assistant_name} Online. Bom dia {self.settings.owner_name}. "
            f"Agora são {current_time}. A temperatura atual é {temperature}. "
            "Deseja programar ou jogar hoje?"
        )
        await self.text_to_speech.speak(greeting)

    async def run(self) -> None:
        await self.bootstrap()
        while True:
            audio = await self.speech_to_text.listen_once()
            transcript = await self.speech_to_text.transcribe(audio)
            if not self.wake_word_detector.is_wake_word_present(transcript):
                continue
            command_text = self.wake_word_detector.remove_wake_word(transcript)
            response_text = await self.process_text(command_text)
            await self.text_to_speech.speak(response_text)
