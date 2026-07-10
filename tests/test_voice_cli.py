from __future__ import annotations

import asyncio
import importlib
import sys
from core.application import ApplicationContainer
from core.config import Settings
from infrastructure.voice.exceptions import MicrophoneUnavailableError
from interfaces.voice_cli import GREETING, run_voice


class FakeRepository:
    async def initialize(self) -> None:
        return None

    async def save_interaction(self, user_text: str, assistant_text: str) -> None:
        return None

    async def get_recent_interactions(self, limit: int = 5) -> list[object]:
        return []


class FakeAudioCapture:
    def __init__(self, *items: object) -> None:
        self.items = list(items)
        self.captured = 0

    async def capture(self) -> object:
        self.captured += 1
        item = self.items.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class FakeSpeechRecognizer:
    def __init__(self, *texts: str) -> None:
        self.texts = list(texts)
        self.audio: list[object] = []

    async def transcribe(self, audio: object) -> str:
        self.audio.append(audio)
        return self.texts.pop(0)


class FakeSpeechSynthesizer:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    async def speak(self, text: str) -> None:
        self.spoken.append(text)


class FakeWakeWordDetector:
    def contains_wake_word(self, text: str) -> bool:
        return "zyron" in text.lower()

    def remove_wake_word(self, text: str) -> str:
        return text.lower().replace("zyron", "").strip(" ,")


class FakeCommandProcessor:
    def __init__(self) -> None:
        self.commands: list[str] = []

    async def process(self, text: str) -> str:
        self.commands.append(text)
        return f"resposta para {text}"


def make_container(settings: Settings, audio: FakeAudioCapture, recognizer: FakeSpeechRecognizer, synthesizer: FakeSpeechSynthesizer, processor: FakeCommandProcessor) -> ApplicationContainer:
    return ApplicationContainer(
        settings=settings,
        repository=FakeRepository(),  # type: ignore[arg-type]
        command_processor=processor,  # type: ignore[arg-type]
        audio_capture=audio,
        speech_recognizer=recognizer,
        speech_synthesizer=synthesizer,
        wake_word_detector=FakeWakeWordDetector(),
    )


def test_voice_loop_speaks_greeting_routes_audio_command_and_response() -> None:
    audio = FakeAudioCapture("audio", "fim")
    recognizer = FakeSpeechRecognizer("que horas são", "sair")
    tts = FakeSpeechSynthesizer()
    processor = FakeCommandProcessor()
    container = make_container(Settings(), audio, recognizer, tts, processor)

    asyncio.run(run_voice(container))

    assert tts.spoken[0] == GREETING
    assert recognizer.audio[0] == "audio"
    assert processor.commands == ["que horas são"]
    assert "resposta para que horas são" in tts.spoken
    assert tts.spoken[-1] == "Encerrando o ZYRON. Até logo."


def test_voice_loop_ignores_empty_text() -> None:
    audio = FakeAudioCapture("silencio", "fim")
    recognizer = FakeSpeechRecognizer("", "sair")
    tts = FakeSpeechSynthesizer()
    processor = FakeCommandProcessor()

    asyncio.run(run_voice(make_container(Settings(), audio, recognizer, tts, processor)))

    assert processor.commands == []


def test_required_wake_word_processes_only_wake_word_commands() -> None:
    settings = Settings(voice_require_wake_word=True)
    audio = FakeAudioCapture("a1", "a2", "fim")
    recognizer = FakeSpeechRecognizer("abra o spotify", "ZYRON, abra o spotify", "sair")
    tts = FakeSpeechSynthesizer()
    processor = FakeCommandProcessor()

    asyncio.run(run_voice(make_container(settings, audio, recognizer, tts, processor)))

    assert processor.commands == ["abra o spotify"]


def test_microphone_error_is_spoken_and_loop_continues() -> None:
    audio = FakeAudioCapture(MicrophoneUnavailableError(), "fim")
    recognizer = FakeSpeechRecognizer("sair")
    tts = FakeSpeechSynthesizer()
    processor = FakeCommandProcessor()

    asyncio.run(run_voice(make_container(Settings(), audio, recognizer, tts, processor)))

    assert "Não consegui acessar o microfone." in tts.spoken
    assert tts.spoken[-1] == "Encerrando o ZYRON. Até logo."


def test_text_cli_does_not_import_voice_libraries() -> None:
    for name in ["faster_whisper", "sounddevice", "edge_tts", "pygame"]:
        sys.modules.pop(name, None)
    importlib.import_module("interfaces.text_cli")
    assert not {"faster_whisper", "sounddevice", "edge_tts", "pygame"}.intersection(sys.modules)


def test_whisper_model_is_initialized_once(monkeypatch) -> None:
    calls = []

    class FakeWhisperModel:
        def __init__(self, *args: object, **kwargs: object) -> None:
            calls.append((args, kwargs))

        def transcribe(self, source: object, language: str) -> tuple[list[object], object]:
            class Segment:
                text = " olá "

            return [Segment()], object()

    import types

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=FakeWhisperModel))
    from infrastructure.voice.speech_recognizer import FasterWhisperSpeechRecognizer

    recognizer = FasterWhisperSpeechRecognizer()
    assert recognizer._transcribe_sync("a") == "olá"
    assert recognizer._transcribe_sync("b") == "olá"
    assert len(calls) == 1


def test_synthesizer_serializes_simultaneous_speech() -> None:
    from infrastructure.voice.speech_synthesizer import EdgeSpeechSynthesizer

    events: list[str] = []

    class FakeSynth(EdgeSpeechSynthesizer):
        async def _speak_locked(self, text: str) -> None:
            events.append(f"start:{text}")
            await asyncio.sleep(0.01)
            events.append(f"end:{text}")

    async def run() -> None:
        synth = FakeSynth()
        await asyncio.gather(synth.speak("um"), synth.speak("dois"))

    asyncio.run(run())
    assert events in (["start:um", "end:um", "start:dois", "end:dois"], ["start:dois", "end:dois", "start:um", "end:um"])
