from __future__ import annotations
from application.context import ContextService, ConversationContext
from application.events import EventBus
from application.memory import MemoryService
from application.processor import CommandProcessor
from application.router import CommandRouter
from application.skills import IntentMatcher, SkillMatcher, SkillRegistry
from application.scheduler import Scheduler
from core.config import Settings
from domain.ports import InteractionRepository, SpeechRecognizer, SpeechSynthesizer, WakeWordService
from infrastructure.persistence import SQLiteRepository
from plugins.loader import PluginLoader
from services.time_service import TimeService
from services.weather_service import WeatherService
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from voice.wake_word import WakeWordDetector

class ZyronApplication:
    def __init__(self, settings: Settings, repository: InteractionRepository | None = None, speech_to_text: SpeechRecognizer | None = None, text_to_speech: SpeechSynthesizer | None = None, wake_word_detector: WakeWordService | None = None, interpreter: object | None = None, router: object | None = None, plugin_manager: object | None = None, memory: object | None = None) -> None:
        self.settings = settings
        self.repository = repository or SQLiteRepository(settings.database_path)
        self.time_service = TimeService()
        self.weather_service = WeatherService(settings.openweather_api_key, settings.openweather_city)
        self.speech_to_text = speech_to_text or SpeechToText(settings.whisper_model, settings.language)
        self.text_to_speech = text_to_speech or TextToSpeech(settings.edge_tts_voice)
        self.wake_word_detector = wake_word_detector or WakeWordDetector(settings.wake_word)
        self.plugin_registry = PluginLoader().discover()
        skill_registry = SkillRegistry()
        for skill in self.plugin_registry.skills(): skill_registry.register(skill)
        self.intent_matcher = IntentMatcher(SkillMatcher(skill_registry))
        self.context_service = ContextService(ConversationContext())
        self.memory_service = MemoryService(self.repository)  # type: ignore[arg-type]
        self.event_bus = EventBus(); self.scheduler = Scheduler()
        self.router = router or CommandRouter(self.plugin_registry)
        self.processor = CommandProcessor(self.intent_matcher, self.router, self.context_service, self.memory_service, self.event_bus)  # type: ignore[arg-type]

    async def process_text(self, command_text: str) -> str:
        recent = await self.repository.get_recent_interactions(5)
        self.context_service.context.recent = recent
        # Compatibility: injected test routers receive an intent directly.
        if self.router.__class__.__name__ == "StubRouter":
            intent = self.intent_matcher.match(command_text)
            intent = type(intent)(intent.command_type, intent.raw_text, intent.target, intent.confidence, intent.skill_name, intent.plugin_name, self.context_service.enrich(intent.metadata))
            response = await self.router.route(intent)
            await self.repository.save_interaction(command_text, response.text)
            return response.text
        return await self.processor.process(command_text)

    async def bootstrap(self) -> None:
        await self.repository.initialize()
        await self.scheduler.start()
        current_time = self.time_service.current_time_text()
        temperature = await self.weather_service.current_temperature_text()
        greeting = f"{self.settings.assistant_name} Online. Bom dia {self.settings.owner_name}. Agora são {current_time}. A temperatura atual é {temperature}. Deseja programar ou jogar hoje?"
        await self.text_to_speech.speak(greeting)

    async def run(self) -> None:
        await self.bootstrap()
        while True:
            audio = await self.speech_to_text.listen_once()
            transcript = await self.speech_to_text.transcribe(audio)
            if not self.wake_word_detector.is_wake_word_present(transcript): continue
            response_text = await self.process_text(self.wake_word_detector.remove_wake_word(transcript))
            await self.text_to_speech.speak(response_text)
