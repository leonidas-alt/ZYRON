from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass
from typing import Any

from zyron.infrastructure.voice.audio_capture import CapturedAudio
from zyron.infrastructure.voice.exceptions import SpeechRecognitionError


@dataclass(frozen=True, slots=True)
class SpeechRecognitionResult:
    text: str
    confidence: float | None = None
    language: str | None = None
    language_probability: float | None = None

    @property
    def recognized(self) -> bool:
        return bool(self.text.strip())


class SpeechRecognizer:
    def __init__(
        self,
        model_name: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str | None = "pt",
        beam_size: int = 5,
        vad_filter: bool = True,
    ) -> None:
        if not model_name.strip():
            raise ValueError(
                "O nome do modelo Whisper não pode estar vazio."
            )

        if not device.strip():
            raise ValueError(
                "O dispositivo do Whisper não pode estar vazio."
            )

        if not compute_type.strip():
            raise ValueError(
                "O compute type do Whisper não pode estar vazio."
            )

        if beam_size <= 0:
            raise ValueError(
                "O beam size deve ser maior que zero."
            )

        self._model_name = model_name.strip()
        self._device = device.strip()
        self._compute_type = compute_type.strip()
        self._language = language.strip() if language else None
        self._beam_size = beam_size
        self._vad_filter = vad_filter
        self._model: Any | None = None

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def device(self) -> str:
        return self._device

    @property
    def compute_type(self) -> str:
        return self._compute_type

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

        audio_array = self._convert_audio_to_float32(audio)
        model = self._get_model()

        try:
            segments_generator, info = model.transcribe(
                audio_array,
                language=self._language,
                beam_size=self._beam_size,
                vad_filter=self._vad_filter,
                condition_on_previous_text=False,
            )

            segments = list(segments_generator)

        except Exception as error:
            raise SpeechRecognitionError(
                "Não foi possível reconhecer o áudio "
                "utilizando o Faster Whisper."
            ) from error

        return SpeechRecognitionResult(
            text=self._combine_segments(segments),
            confidence=self._calculate_confidence(segments),
            language=getattr(
                info,
                "language",
                self._language,
            ),
            language_probability=self._safe_float(
                getattr(
                    info,
                    "language_probability",
                    None,
                )
            ),
        )

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model

        whisper_model_class = self._load_whisper_model_class()

        try:
            self._model = whisper_model_class(
                self._model_name,
                device=self._device,
                compute_type=self._compute_type,
            )

        except Exception as error:
            raise SpeechRecognitionError(
                "Não foi possível carregar o modelo Faster Whisper."
            ) from error

        return self._model

    def _convert_audio_to_float32(
        self,
        audio: CapturedAudio,
    ) -> Any:
        try:
            import numpy as np

        except ImportError as error:
            raise SpeechRecognitionError(
                "A biblioteca numpy não está instalada."
            ) from error

        try:
            samples = np.frombuffer(
                audio.data,
                dtype=np.int16,
            )

            return samples.astype(np.float32) / 32768.0

        except Exception as error:
            raise SpeechRecognitionError(
                "Não foi possível converter o áudio."
            ) from error

    def _combine_segments(
        self,
        segments: list[Any],
    ) -> str:
        text_parts: list[str] = []

        for segment in segments:
            text = str(
                getattr(
                    segment,
                    "text",
                    "",
                )
            ).strip()

            if text:
                text_parts.append(text)

        return " ".join(text_parts).strip()

    def _calculate_confidence(
        self,
        segments: list[Any],
    ) -> float | None:
        probabilities: list[float] = []

        for segment in segments:
            average_log_probability = self._safe_float(
                getattr(
                    segment,
                    "avg_logprob",
                    None,
                )
            )

            if average_log_probability is None:
                continue

            try:
                probability = math.exp(
                    average_log_probability
                )

                probabilities.append(
                    max(
                        0.0,
                        min(
                            probability,
                            1.0,
                        ),
                    )
                )

            except (OverflowError, ValueError):
                continue

        if not probabilities:
            return None

        return sum(probabilities) / len(probabilities)

    def _validate_audio(
        self,
        audio: CapturedAudio,
    ) -> None:
        if not audio.data:
            raise SpeechRecognitionError(
                "Nenhum áudio foi fornecido."
            )

        if audio.sample_rate != 16_000:
            raise SpeechRecognitionError(
                "O áudio precisa estar em 16 kHz."
            )

        if audio.channels != 1:
            raise SpeechRecognitionError(
                "O áudio precisa estar em canal mono."
            )

        if audio.sample_width != 2:
            raise SpeechRecognitionError(
                "O áudio precisa estar em PCM de 16 bits."
            )

    def _load_whisper_model_class(self) -> Any:
        try:
            from faster_whisper import WhisperModel

        except ImportError as error:
            raise SpeechRecognitionError(
                "A biblioteca faster-whisper não está instalada."
            ) from error

        return WhisperModel

    @staticmethod
    def _safe_float(
        value: object,
    ) -> float | None:
        if isinstance(value, (int, float)):
            return float(value)

        return None
