"""
ROADMAP DO MÓDULO

Versão Atual:

* Orquestra dependências, saudação inicial, loop de escuta e roteamento.

Próxima Versão:

* Adicionar tratamento resiliente de erros, logging estruturado e lifecycle hooks.

Versão Futura:

* Sistema de plugins, multiusuário, filas de eventos e painel administrativo.

Dependências Futuras:

* Plugin manager, Dashboard Web, PostgreSQL, AWS
"""

# TODO:
# Criar testes de ciclo de vida cobrindo bootstrap, roteamento, persistência e fala com dependências mockadas.
# FIXME:
# O loop principal ainda pode parar se STT, TTS, banco, clima ou Ollama lançarem exceções.
# IMPROVEMENT:
# Introduzir interfaces para STT, TTS, IA, repositório e roteador, reduzindo acoplamento da aplicação concreta.
# FUTURE:
# Adicionar sistema de plugins, múltiplos usuários, dashboard web, painel administrativo e filas assíncronas de comandos.
# OPTIMIZATION:
# Usar execução assíncrona ou filas para não bloquear escuta enquanto comandos longos são processados.
# SECURITY:
# Inserir uma camada de autorização antes de executar automações, e-mails, agenda, finanças ou comandos shell.


"""Main application orchestration for the ZYRON assistant."""

from ai.ollama_client import OllamaClient
from automation.app_launcher import AppLauncher
from automation.browser_controller import BrowserController
from commands.command_interpreter import CommandInterpreter
from commands.command_router import CommandRouter
from core.config import Settings
from database.sqlite_repository import SQLiteRepository
from services.time_service import TimeService
from services.weather_service import WeatherService
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from voice.wake_word import WakeWordDetector


class ZyronApplication:
    """Coordinates startup, listening, command routing and speaking responses."""

    def __init__(self, settings: Settings) -> None:
        """Initialize all application services using dependency injection."""
        self.settings = settings
        self.repository = SQLiteRepository(settings.database_path)
        self.time_service = TimeService()
        self.weather_service = WeatherService(settings.openweather_api_key, settings.openweather_city)
        self.ai_client = OllamaClient(settings.ollama_base_url, settings.ollama_model)
        self.speech_to_text = SpeechToText(settings.whisper_model, settings.language)
        self.text_to_speech = TextToSpeech(settings.edge_tts_voice)
        self.wake_word_detector = WakeWordDetector(settings.wake_word)
        self.interpreter = CommandInterpreter()
        self.router = CommandRouter(
            ai_client=self.ai_client,
            app_launcher=AppLauncher(),
            browser_controller=BrowserController(),
            time_service=self.time_service,
            weather_service=self.weather_service,
        )

    def bootstrap(self) -> None:
        """Prepare local resources and greet the owner on application startup."""
        self.repository.initialize()
        current_time = self.time_service.current_time_text()
        temperature = self.weather_service.current_temperature_text()
        greeting = (
            f"{self.settings.assistant_name} Online. Bom dia {self.settings.owner_name}. "
            f"Agora são {current_time}. A temperatura atual é {temperature}. "
            "Deseja programar ou jogar hoje?"
        )
        self.text_to_speech.speak(greeting)

    def run(self) -> None:
        """Run the background assistant loop until the process is stopped."""
        self.bootstrap()
        while True:
            audio = self.speech_to_text.listen_once()
            transcript = self.speech_to_text.transcribe(audio)
            if not self.wake_word_detector.is_wake_word_present(transcript):
                continue
            command_text = self.wake_word_detector.remove_wake_word(transcript)
            intent = self.interpreter.interpret(command_text)
            response = self.router.route(intent)
            self.repository.save_interaction(command_text, response.text)
            if response.spoken:
                self.text_to_speech.speak(response.text)
