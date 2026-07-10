from __future__ import annotations
import asyncio
from typing import Any
from faster_whisper import WhisperModel
from core.ports import SpeechRecognizer


class SpeechToText(SpeechRecognizer):
    def __init__(self, model_name: str, language: str) -> None:
        self.model_name = model_name
        self.language = language
        self._model: WhisperModel | None = None

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        return self._model

    async def listen_once(self) -> Any:
        return None

    async def transcribe(self, audio: Any) -> str:
        if audio is None:
            return ""
        return await asyncio.to_thread(self._transcribe_sync, audio)

    def _transcribe_sync(self, audio: Any) -> str:
        segments, _ = self.model.transcribe(audio, language=self.language[:2])
        return " ".join(segment.text.strip() for segment in segments).strip()
