from __future__ import annotations

import asyncio
from typing import Any

from application.ports import SpeechRecognizerPort
from infrastructure.voice.audio_capture import CapturedAudio
from infrastructure.voice.exceptions import TranscriptionError


class FasterWhisperSpeechRecognizer(SpeechRecognizerPort):
    def __init__(self, model_name: str = "small", language: str = "pt", device: str = "cpu", compute_type: str = "int8") -> None:
        self.model_name = model_name
        self.language = language
        self.device = device
        self.compute_type = compute_type
        self._model: Any | None = None

    @property
    def model(self) -> Any:
        if self._model is None:
            try:
                from faster_whisper import WhisperModel

                self._model = WhisperModel(self.model_name, device=self.device, compute_type=self.compute_type)
            except Exception as exc:
                raise TranscriptionError("Não consegui inicializar o modelo Whisper.") from exc
        return self._model

    def warm_up(self) -> None:
        _ = self.model

    async def transcribe(self, audio: Any) -> str:
        if audio is None:
            return ""
        return await asyncio.to_thread(self._transcribe_sync, audio)

    def _transcribe_sync(self, audio: Any) -> str:
        try:
            source = audio.samples if isinstance(audio, CapturedAudio) else audio
            segments, _ = self.model.transcribe(source, language=self.language)
            text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
            return " ".join(text.split())
        except TranscriptionError:
            raise
        except Exception as exc:
            raise TranscriptionError("Falha ao transcrever o áudio capturado.") from exc
