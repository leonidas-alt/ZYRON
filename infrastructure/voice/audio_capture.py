from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from application.ports import AudioCapturePort
from infrastructure.voice.exceptions import AudioCaptureError, MicrophoneUnavailableError


@dataclass(frozen=True)
class CapturedAudio:
    samples: Any
    sample_rate: int


class SoundDeviceAudioCapture(AudioCapturePort):
    def __init__(
        self,
        device: str | int | None = None,
        sample_rate: int = 16000,
        channels: int = 1,
        max_duration_seconds: float = 10.0,
        silence_duration_seconds: float = 1.5,
        silence_threshold: float = 0.01,
    ) -> None:
        self.device = device if device not in {"", None} else None
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_duration_seconds = max_duration_seconds
        self.silence_duration_seconds = silence_duration_seconds
        self.silence_threshold = silence_threshold

    async def capture(self) -> CapturedAudio:
        return await asyncio.to_thread(self._capture_sync)

    def verify_microphone(self) -> None:
        self._resolve_input_device()

    def _resolve_input_device(self) -> Any:
        try:
            import sounddevice as sd

            if self.device is not None:
                info = sd.query_devices(self.device, "input")
            else:
                info = sd.query_devices(kind="input")
        except Exception as exc:
            raise MicrophoneUnavailableError("Não consegui acessar o microfone padrão.") from exc
        if not info or int(info.get("max_input_channels", 0)) <= 0:
            raise MicrophoneUnavailableError("Nenhum microfone de entrada foi encontrado.")
        return info

    def _capture_sync(self) -> CapturedAudio:
        self._resolve_input_device()
        try:
            import numpy as np
            import sounddevice as sd
        except Exception as exc:
            raise AudioCaptureError("Dependências de captura de áudio não estão instaladas.") from exc

        chunks: list[Any] = []
        block_size = max(1, int(self.sample_rate * 0.1))
        max_blocks = max(1, int(self.max_duration_seconds * self.sample_rate / block_size))
        silence_blocks_needed = max(1, int(self.silence_duration_seconds * self.sample_rate / block_size))
        silent_blocks = 0
        heard_voice = False

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                device=self.device,
                blocksize=block_size,
            ) as stream:
                for _ in range(max_blocks):
                    data, overflowed = stream.read(block_size)
                    if overflowed:
                        raise AudioCaptureError("O buffer do microfone estourou durante a gravação.")
                    chunks.append(data.copy())
                    level = float(np.sqrt(np.mean(np.square(data)))) if data.size else 0.0
                    if level >= self.silence_threshold:
                        heard_voice = True
                        silent_blocks = 0
                    elif heard_voice:
                        silent_blocks += 1
                        if silent_blocks >= silence_blocks_needed:
                            break
        except MicrophoneUnavailableError:
            raise
        except Exception as exc:
            raise MicrophoneUnavailableError("Microfone indisponível, ocupado ou sem permissão.") from exc

        if not chunks:
            raise AudioCaptureError("A gravação do microfone ficou vazia.")
        samples = np.concatenate(chunks, axis=0).astype("float32")
        if samples.size == 0:
            raise AudioCaptureError("A gravação do microfone ficou vazia.")
        return CapturedAudio(samples=samples.squeeze(), sample_rate=self.sample_rate)
