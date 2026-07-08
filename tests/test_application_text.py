from __future__ import annotations
import asyncio
from datetime import UTC, datetime
from core.application import ZyronApplication
from core.config import Settings
from core.models import AssistantResponse, CommandIntent, Interaction


class StubRepository:
    def __init__(self) -> None:
        self.interactions = [Interaction("olá", "Olá!", datetime.now(UTC))]
        self.saved: list[tuple[str, str]] = []

    async def initialize(self) -> None:
        return None

    async def save_interaction(self, user_text: str, assistant_text: str) -> None:
        self.saved.append((user_text, assistant_text))

    async def get_recent_interactions(self, limit: int = 5) -> list[Interaction]:
        return self.interactions[-limit:]


class StubRouter:
    def __init__(self) -> None:
        self.intent: CommandIntent | None = None

    async def route(self, intent: CommandIntent) -> AssistantResponse:
        self.intent = intent
        return AssistantResponse("resposta simples")


class StubSpeechToText:
    async def listen_once(self) -> None:
        return None

    async def transcribe(self, audio: object) -> str:
        return ""


class StubTextToSpeech:
    async def speak(self, text: str) -> None:
        return None


class StubWakeWordDetector:
    def is_wake_word_present(self, text: str) -> bool:
        return False

    def remove_wake_word(self, text: str) -> str:
        return text


def test_process_text_routes_command_with_context_and_saves_interaction() -> None:
    repository = StubRepository()
    router = StubRouter()
    app = ZyronApplication(
        settings=Settings(),
        repository=repository,
        speech_to_text=StubSpeechToText(),
        text_to_speech=StubTextToSpeech(),
        wake_word_detector=StubWakeWordDetector(),
        router=router,  # type: ignore[arg-type]
    )

    response = asyncio.run(app.process_text("como estou?"))

    assert response == "resposta simples"
    assert repository.saved == [("como estou?", "resposta simples")]
    assert router.intent is not None
    assert "Usuário: olá" in router.intent.metadata["conversation_context"]
