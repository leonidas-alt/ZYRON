from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from zyron.infrastructure.voice.audio_capture import CapturedAudio
from zyron.infrastructure.voice.exceptions import SpeechRecognitionError


@dataclass(frozen=True, slots=True)
class SpeechRecognitionResult:
    text: str
    confidence: float | None = None

    @property
    def recognized(self) -> bool:
        return bool(self.text.strip())


class SpeechRecognizer:
    def __init__(
        self,
        model_path: str | Path,
    ) -> None:
        self._model_path = Path(model_path)
        self._model: Any | None = None

    @property
    def model_path(self) -> Path:
        return self._model_path

    async def recognize(
        self,
        audio: CapturedAudio,
    ) -> SpeechRecognitionResult:
        return await asyncio.to_thread(
            self.recognize_sync,
            audio,
        )

    def recognize_sync(
        self,
        audio: CapturedAudio,
    ) -> SpeechRecognitionResult:
        self._validate_audio(audio)

        model = self._get_model()
        recognizer_class = self._load_recognizer_class()

        try:
            recognizer = recognizer_class(
                model,
                float(audio.sample_rate),
            )

            recognizer.SetWords(True)
            recognizer.AcceptWaveform(audio.data)

            raw_result = recognizer.FinalResult()
        except Exception as error:
            raise SpeechRecognitionError(
                "Não foi possível reconhecer o áudio capturado."
            ) from error

        return self._parse_result(raw_result)

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model

        if not self._model_path.exists():
            raise SpeechRecognitionError(
                f"O modelo de reconhecimento não foi encontrado: "
                f"{self._model_path}"
            )

        if not self._model_path.is_dir():
            raise SpeechRecognitionError(
                "O caminho do modelo de reconhecimento deve ser uma pasta."
            )

        model_class = self._load_model_class()

        try:
            self._model = model_class(
                str(self._model_path)
            )
        except Exception as error:
            raise SpeechRecognitionError(
                "Não foi possível carregar o modelo de reconhecimento."
            ) from error

        return self._model

    def _parse_result(
        self,
        raw_result: str,
    ) -> SpeechRecognitionResult:
        try:
            result = json.loads(raw_result)
        except json.JSONDecodeError as error:
            raise SpeechRecognitionError(
                "O reconhecedor retornou uma resposta inválida."
            ) from error

        text = str(
            result.get("text", "")
        ).strip()

        confidence = self._calculate_confidence(
            result.get("result")
        )

        return SpeechRecognitionResult(
            text=text,
            confidence=confidence,
        )

    def _calculate_confidence(
        self,
        words: object,
    ) -> float | None:
        if not isinstance(words, list):
            return None

        confidence_values: list[float] = []

        for word in words:
            if not isinstance(word, dict):
                continue

            confidence = word.get("conf")

            if isinstance(confidence, int | float):
                confidence_values.append(
                    float(confidence)
                )

        if not confidence_values:
            return None

        return sum(confidence_values) / len(
            confidence_values
        )

    def _validate_audio(
        self,
        audio: CapturedAudio,
    ) -> None:
        if not audio.data:
            raise SpeechRecognitionError(
                "Nenhum áudio foi fornecido para reconhecimento."
            )

        if audio.sample_rate <= 0:
            raise SpeechRecognitionError(
                "A taxa de amostragem do áudio é inválida."
            )

        if audio.channels != 1:
            raise SpeechRecognitionError(
                "O reconhecimento exige áudio em canal mono."
            )

        if audio.sample_width != 2:
            raise SpeechRecognitionError(
                "O reconhecimento exige áudio PCM de 16 bits."
            )

    def _load_model_class(self) -> Any:
        try:
            from vosk import Model
        except ImportError as error:
            raise SpeechRecognitionError(
                "A biblioteca vosk não está instalada."
            ) from error

        return Model

    def _load_recognizer_class(self) -> Any:
        try:
            from vosk import KaldiRecognizer
        except ImportError as error:
            raise SpeechRecognitionError(
                "A biblioteca vosk não está instalada."
            ) from error

        return KaldiRecognizer
