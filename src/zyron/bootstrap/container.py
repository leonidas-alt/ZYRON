from __future__ import annotations

from dataclasses import dataclass

from zyron.application.assistant import ZyronAssistant
from zyron.application.confirmations import ConfirmationService
from zyron.application.context.conversation import ConversationContext
from zyron.application.permissions.service import PermissionService
from zyron.config.settings import Settings
from zyron.infrastructure.ai.ollama_client import OllamaClient
from zyron.infrastructure.persistence.sqlite_repository import SQLiteRepository
from zyron.infrastructure.voice.audio_capture import AudioCapture
from zyron.infrastructure.voice.speech_recognizer import SpeechRecognizer
from zyron.infrastructure.voice.speech_synthesizer import SpeechSynthesizer
from zyron.infrastructure.voice.wake_word_detector import WakeWordDetector
from zyron.plugins.loader import PluginLoadResult, PluginLoader
from zyron.plugins.registry import PluginRegistry


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    settings: Settings
    assistant: ZyronAssistant
    conversation_context: ConversationContext
    permissions: PermissionService
    confirmation_service: ConfirmationService
    repository: SQLiteRepository
    plugin_registry: PluginRegistry
    plugin_load_result: PluginLoadResult
    audio_capture: AudioCapture
    speech_recognizer: SpeechRecognizer
    speech_synthesizer: SpeechSynthesizer
    wake_word_detector: WakeWordDetector


def build_container(
    settings: Settings | None = None,
) -> ApplicationContainer:
    resolved_settings = settings or Settings.from_env()

    repository = SQLiteRepository(
        database_path=resolved_settings.database_path,
    )

    conversation_context = ConversationContext(
        repository=repository,
        history_limit=10,
    )

    ai_client = OllamaClient(
        base_url=resolved_settings.ollama_base_url,
        model=resolved_settings.ollama_model,
        timeout_seconds=resolved_settings.ollama_timeout_seconds,
    )

    assistant = ZyronAssistant(
        ai_client=ai_client,
        assistant_name=resolved_settings.assistant_name,
        owner_name=resolved_settings.owner_name,
        conversation_context=conversation_context,
    )

    permissions = PermissionService()

    confirmation_service = ConfirmationService(
        timeout_seconds=30,
    )

    plugin_registry = PluginRegistry()

    plugin_loader = PluginLoader(
        registry=plugin_registry,
    )

    plugin_load_result = plugin_loader.load_plugins(
        initialize=True,
        enable=False,
    )

    audio_capture = AudioCapture(
        sample_rate=resolved_settings.audio_sample_rate,
        channels=resolved_settings.audio_channels,
        dtype=resolved_settings.audio_dtype,
        device=resolved_settings.audio_device,
    )

    speech_recognizer = SpeechRecognizer(
        model_name=resolved_settings.whisper_model,
        device=resolved_settings.whisper_device,
        compute_type=resolved_settings.whisper_compute_type,
        language=resolved_settings.whisper_language,
        beam_size=resolved_settings.whisper_beam_size,
        vad_filter=resolved_settings.whisper_vad_filter,
    )

    speech_synthesizer = SpeechSynthesizer(
        rate=resolved_settings.voice_rate,
        volume=resolved_settings.voice_volume,
        voice_name=resolved_settings.voice_name,
    )

    wake_word_detector = WakeWordDetector(
        wake_words=resolved_settings.wake_words,
    )

    return ApplicationContainer(
        settings=resolved_settings,
        assistant=assistant,
        conversation_context=conversation_context,
        permissions=permissions,
        confirmation_service=confirmation_service,
        repository=repository,
        plugin_registry=plugin_registry,
        plugin_load_result=plugin_load_result,
        audio_capture=audio_capture,
        speech_recognizer=speech_recognizer,
        speech_synthesizer=speech_synthesizer,
        wake_word_detector=wake_word_detector,
    )
