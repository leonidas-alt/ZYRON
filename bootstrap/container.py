from __future__ import annotations
from dataclasses import dataclass
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from application.context import ContextService, ConversationContext
from application.events import EventBus
from application.memory import MemoryService
from application.ports import AudioCapturePort, SpeechRecognizerPort, SpeechSynthesizerPort, WakeWordDetectorPort
from application.processor import CommandProcessor, IntentRouter
from application.router import CommandRouter
from application.scheduler import Scheduler
from application.skills import IntentMatcher, SkillMatcher, SkillRegistry
from automation.app_launcher import AppLauncher
from automation.browser_controller import BrowserController
from core.config import Settings
from domain.ports import InteractionRepository
from infrastructure.persistence import SQLiteRepository
from plugins.loader import PluginLoader
from services.time_service import TimeService
from services.weather_service import WeatherService

def configure_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    root = logging.getLogger()
    if root.handlers: return
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    console = logging.StreamHandler(); console.setFormatter(fmt)
    file = RotatingFileHandler("logs/zyron.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"); file.setFormatter(fmt)
    root.addHandler(console); root.addHandler(file)

@dataclass
class ApplicationContainer:
    settings: Settings; repository: InteractionRepository; command_processor: CommandProcessor; memory_service: MemoryService | None = None; context_service: ContextService | None = None; skill_registry: SkillRegistry | None = None; plugin_registry: object | None = None; browser_controller: BrowserController | None = None; application_launcher: AppLauncher | None = None; audio_capture: AudioCapturePort | None = None; speech_recognizer: SpeechRecognizerPort | None = None; speech_synthesizer: SpeechSynthesizerPort | None = None; wake_word_detector: WakeWordDetectorPort | None = None; scheduler: Scheduler | None = None
    async def initialize(self) -> None:
        await self.repository.initialize()
        if self.scheduler is not None: await self.scheduler.start()
        try:
            if self.speech_recognizer is not None and hasattr(self.speech_recognizer, "warm_up"): self.speech_recognizer.warm_up()  # type: ignore[attr-defined]
            if self.audio_capture is not None and hasattr(self.audio_capture, "verify_microphone"): self.audio_capture.verify_microphone()  # type: ignore[attr-defined]
        except Exception: logging.getLogger(__name__).exception("Falha ao inicializar componente de voz")

def build_base_container(settings: Settings, repository: InteractionRepository | None = None, router: IntentRouter | None = None) -> ApplicationContainer:
    configure_logging()
    repository = repository or SQLiteRepository(settings.database_path)
    memory_service = MemoryService(repository)  # type: ignore[arg-type]
    context_service = ContextService(ConversationContext())
    browser_controller = BrowserController(); application_launcher = AppLauncher()
    deps = {"memory_service": memory_service, "browser_controller": browser_controller, "application_launcher": application_launcher, "time_provider": TimeService(), "weather_provider": WeatherService(settings.openweather_api_key, settings.openweather_city)}
    plugin_registry = PluginLoader(dependencies=deps).discover()
    skill_registry = SkillRegistry()
    for plugin_skill in plugin_registry.skills(): skill_registry.register(plugin_skill)
    processor = CommandProcessor(IntentMatcher(SkillMatcher(skill_registry)), router or CommandRouter(plugin_registry), context_service, memory_service, EventBus())
    return ApplicationContainer(settings=settings, repository=repository, command_processor=processor, memory_service=memory_service, context_service=context_service, skill_registry=skill_registry, plugin_registry=plugin_registry, browser_controller=browser_controller, application_launcher=application_launcher, scheduler=Scheduler())

def build_text_container(settings: Settings) -> ApplicationContainer: return build_base_container(settings)

def build_voice_container(settings: Settings) -> ApplicationContainer:
    from infrastructure.voice.audio_capture import SoundDeviceAudioCapture
    from infrastructure.voice.speech_recognizer import FasterWhisperSpeechRecognizer
    from infrastructure.voice.speech_synthesizer import EdgeSpeechSynthesizer
    from infrastructure.voice.wake_word_detector import TextWakeWordDetector
    c = build_base_container(settings)
    c.audio_capture = SoundDeviceAudioCapture(settings.microphone_device, settings.audio_sample_rate, settings.audio_channels, settings.audio_max_duration_seconds, settings.audio_silence_duration_seconds)
    c.speech_recognizer = FasterWhisperSpeechRecognizer(settings.whisper_model, settings.whisper_language, settings.whisper_device, settings.whisper_compute_type)
    c.speech_synthesizer = EdgeSpeechSynthesizer(settings.tts_voice, settings.tts_rate, settings.tts_volume)
    c.wake_word_detector = TextWakeWordDetector(settings.voice_wake_word)
    return c
