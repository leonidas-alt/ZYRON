from __future__ import annotations

import asyncio
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from zyron.infrastructure.voice.exceptions import AudioCaptureError


@dataclass(frozen=True, slots=True)
class CapturedAudio:
    data: bytes
    sample_rate: int
    channels: int
    sample_width: int

    @property
    def duration_seconds(self) -> float:
        frame_size = self.channels * self.sample_width

        if frame_size <= 0 or self.sample_rate <= 0:
            return 0.0

        frame_count = len(self.data) / frame_size

        return frame_count / self.sample_rate

    def save(self, output_path: str | Path) -> Path:
        resolved_path = Path(output_path)
        resolved_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            with wave.open(
                str(resolved_path),
                "wb",
            ) as audio_file:
                audio_file.setnchannels(self.channels)
                audio_file.setsampwidth(self.sample_width)
                audio_file.setframerate(self.sample_rate)
                audio_file.writeframes(self.data)
        except Exception as error:
            raise AudioCaptureError(
                "Não foi possível salvar o áudio capturado."
            ) from error

        return resolved_path


class AudioCapture:
    def __init__(
        self,
        sample_rate: int = 16_000,
        channels: int = 1,
        dtype: str = "int16",
        device: int | str | None = None,
    ) -> None:
        if sample_rate <= 0:
            raise ValueError(
                "A taxa de amostragem deve ser maior que zero."
            )

        if channels <= 0:
            raise ValueError(
                "A quantidade de canais deve ser maior que zero."
            )

        self._sample_rate = sample_rate
        self._channels = channels
        self._dtype = dtype
        self._device = device

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def channels(self) -> int:
        return self._channels

    @property
    def device(self) -> int | str | None:
        return self._device

    async def record(
        self,
        duration_seconds: float,
    ) -> CapturedAudio:
        if duration_seconds <= 0:
            raise ValueError(
                "A duração da gravação deve ser maior que zero."
            )

        return await asyncio.to_thread(
            self.record_sync,
            duration_seconds,
        )

    def record_sync(
        self,
        duration_seconds: float,
    ) -> CapturedAudio:
        if duration_seconds <= 0:
            raise ValueError(
                "A duração da gravação deve ser maior que zero."
            )

        sounddevice = self._load_sounddevice()

        frame_count = int(
            duration_seconds * self._sample_rate
        )

        try:
            recording = sounddevice.rec(
                frames=frame_count,
                samplerate=self._sample_rate,
                channels=self._channels,
                dtype=self._dtype,
                device=self._device,
            )

            sounddevice.wait()
        except Exception as error:
            raise AudioCaptureError(
                "Não foi possível capturar áudio do microfone."
            ) from error

        try:
            audio_data = recording.tobytes()
            sample_width = recording.dtype.itemsize
        except Exception as error:
            raise AudioCaptureError(
                "O áudio capturado possui um formato inválido."
            ) from error

        if not audio_data:
            raise AudioCaptureError(
                "Nenhum áudio foi capturado."
            )

        return CapturedAudio(
            data=audio_data,
            sample_rate=self._sample_rate,
            channels=self._channels,
            sample_width=sample_width,
        )

    def list_devices(self) -> list[dict[str, Any]]:
        sounddevice = self._load_sounddevice()

        try:
            devices = sounddevice.query_devices()
        except Exception as error:
            raise AudioCaptureError(
                "Não foi possível consultar os dispositivos de áudio."
            ) from error

        result: list[dict[str, Any]] = []

        for index, device in enumerate(devices):
            result.append(
                {
                    "index": index,
                    "name": str(device["name"]),
                    "input_channels": int(
                        device["max_input_channels"]
                    ),
                    "output_channels": int(
                        device["max_output_channels"]
                    ),
                    "default_sample_rate": float(
                        device["default_samplerate"]
                    ),
                }
            )

        return result

    def list_input_devices(
        self,
    ) -> list[dict[str, Any]]:
        return [
            device
            for device in self.list_devices()
            if device["input_channels"] > 0
        ]

    def get_default_input_device(
        self,
    ) -> dict[str, Any]:
        sounddevice = self._load_sounddevice()

        try:
            default_devices = sounddevice.default.device
            input_device_index = int(default_devices[0])
            device = sounddevice.query_devices(
                input_device_index,
                "input",
            )
        except Exception as error:
            raise AudioCaptureError(
                "Não foi possível identificar o microfone padrão."
            ) from error

        return {
            "index": input_device_index,
            "name": str(device["name"]),
            "input_channels": int(
                device["max_input_channels"]
            ),
            "default_sample_rate": float(
                device["default_samplerate"]
            ),
        }

    def _load_sounddevice(self) -> Any:
        try:
            import sounddevice
        except ImportError as error:
            raise AudioCaptureError(
                "A biblioteca sounddevice não está instalada."
            ) from error

        return sounddevice
