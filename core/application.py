from __future__ import annotations

from ai.ollama_client import OllamaClient
from automation.app_launcher import AppLauncher
from automation.browser_controller import BrowserController
from commands.command_interpreter import CommandInterpreter
from commands.command_router import CommandRouter
from commands.factory import CommandFactory
from core.config import Settings
from core.ports import (
    CommandInterpreterPort,
    InteractionRepository,
    SpeechRecognizer,
    SpeechSynthesizer,
    WakeWordService,
)
from database.sqlite_repository import SQLiteRepository
from services.time_service import TimeService
from services.weather_service import WeatherService
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from voice.wake_word import WakeWordDetector


class ZyronApplication:

    def __init__(
        self,
        settings: Settings,
        repository: InteractionRepository | None = None,
        speech_to_text: SpeechRecognizer | None = None,
        text_to_speech: SpeechSynthesizer | None = None,
        wake_word_detector: WakeWordService | None = None,
        interpreter: CommandInterpreterPort | None = None,
        router: CommandRouter | None = None,
    ) -> None:
        self.settings = settings
        self.repository = repository or SQLiteRepository(settings.database_path)
        self.time_service = TimeService()
        self.weather_service = WeatherService(settings.openweather_api_key, settings.openweather_city)
        self.speech_to_text = speech_to_text or SpeechToText(settings.whisper_model, settings.language)
        self.text_to_speech = text_to_speech or TextToSpeech(settings.edge_tts_voice)
        self.wake_word_detector = wake_word_detector or WakeWordDetector(settings.wake_word)
        self.interpreter = interpreter or CommandInterpreter()
        self.router = router or self._build_router(settings)

    def _build_router(self, settings: Settings) -> CommandRouter:
        command_factory = CommandFactory(
            ai_client=OllamaClient(settings.ollama_base_url, settings.ollama_model),
            app_launcher=AppLauncher(),
            browser_controller=BrowserController(),
            time_service=self.time_service,
            weather_service=self.weather_service,
        )
        return CommandRouter(command_factory)

    async def bootstrap(self) -> None:
        await self.repository.initialize()
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
            intent = self.interpreter.interpret(command_text)
            response = await self.router.route(intent)
            await self.repository.save_interaction(command_text, response.text)
            if response.spoken:
                await self.text_to_speech.speak(response.text)
