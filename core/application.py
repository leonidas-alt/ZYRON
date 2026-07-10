from __future__ import annotations

from dataclasses import dataclass

from application.context import ContextService, ConversationContext
from application.events import EventBus
from application.memory import MemoryService
from application.ports import AudioCapturePort, SpeechRecognizerPort, SpeechSynthesizerPort, WakeWordDetectorPort
from application.processor import CommandProcessor, IntentRouter
from application.router import CommandRouter
from application.scheduler import Scheduler
from application.skills import IntentMatcher, SkillMatcher, SkillRegistry
from core.config import Settings
from domain.ports import InteractionRepository
from infrastructure.persistence import SQLiteRepository
from plugins.loader import PluginLoader


@dataclass
class ApplicationContainer:
    settings: Settings
    repository: InteractionRepository
    command_processor: CommandProcessor
    audio_capture: AudioCapturePort | None = None
    speech_recognizer: SpeechRecognizerPort | None = None
    speech_synthesizer: SpeechSynthesizerPort | None = None
    wake_word_detector: WakeWordDetectorPort | None = None
    scheduler: Scheduler | None = None

    async def initialize(self) -> None:
        await self.repository.initialize()
        if self.scheduler is not None:
            await self.scheduler.start()
        if self.speech_recognizer is not None and hasattr(self.speech_recognizer, "warm_up"):
            self.speech_recognizer.warm_up()  # type: ignore[attr-defined]
        if self.audio_capture is not None and hasattr(self.audio_capture, "verify_microphone"):
            self.audio_capture.verify_microphone()  # type: ignore[attr-defined]


class ZyronApplication:
    def __init__(
        self,
        settings: Settings,
        repository: InteractionRepository | None = None,
        speech_to_text: object | None = None,
        text_to_speech: object | None = None,
        wake_word_detector: object | None = None,
        interpreter: object | None = None,
        router: IntentRouter | None = None,
        plugin_manager: object | None = None,
        memory: object | None = None,
    ) -> None:
        self.container = _build_base_container(settings, repository=repository, router=router)
        self.settings = settings
        self.repository = self.container.repository
        self.processor = self.container.command_processor

    async def process_text(self, command_text: str) -> str:
        context_service = self.processor._context  # compatibility for existing public facade
        context_service.context.recent = await self.repository.get_recent_interactions(5)
        return await self.processor.process(command_text)


def _build_base_container(settings: Settings, repository: InteractionRepository | None = None, router: IntentRouter | None = None) -> ApplicationContainer:
    repository = repository or SQLiteRepository(settings.database_path)
    plugin_registry = PluginLoader().discover()
    skill_registry = SkillRegistry()
    for plugin_skill in plugin_registry.skills():
        skill_registry.register(plugin_skill)
    intent_matcher = IntentMatcher(SkillMatcher(skill_registry))
    context_service = ContextService(ConversationContext())
    memory_service = MemoryService(repository)  # type: ignore[arg-type]
    event_bus = EventBus()
    command_router = router or CommandRouter(plugin_registry)
    processor = CommandProcessor(intent_matcher, command_router, context_service, memory_service, event_bus)
    return ApplicationContainer(settings=settings, repository=repository, command_processor=processor, scheduler=Scheduler())


def build_text_container(settings: Settings) -> ApplicationContainer:
    return _build_base_container(settings)


def build_voice_container(settings: Settings) -> ApplicationContainer:
    from infrastructure.voice.audio_capture import SoundDeviceAudioCapture
    from infrastructure.voice.speech_recognizer import FasterWhisperSpeechRecognizer
    from infrastructure.voice.speech_synthesizer import EdgeSpeechSynthesizer
    from infrastructure.voice.wake_word_detector import TextWakeWordDetector

    container = _build_base_container(settings)
    container.audio_capture = SoundDeviceAudioCapture(
        device=settings.microphone_device,
        sample_rate=settings.audio_sample_rate,
        channels=settings.audio_channels,
        max_duration_seconds=settings.audio_max_duration_seconds,
        silence_duration_seconds=settings.audio_silence_duration_seconds,
    )
    container.speech_recognizer = FasterWhisperSpeechRecognizer(
        model_name=settings.whisper_model,
        language=settings.whisper_language,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
    )
    container.speech_synthesizer = EdgeSpeechSynthesizer(settings.tts_voice, settings.tts_rate, settings.tts_volume)
    container.wake_word_detector = TextWakeWordDetector(settings.voice_wake_word)
    return container
