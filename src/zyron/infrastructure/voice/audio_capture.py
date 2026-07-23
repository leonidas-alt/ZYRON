from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from zyron.infrastructure.voice.exceptions import AudioCaptureError


@dataclass(frozen=True, slots=True)
class CapturedAudio:
    data: bytes
    sample_rate: int
    channels: int
    sample_width: int
    duration_seconds: float

    @property
    def empty(self) -> bool:
        return not self.data


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

        if dtype != "int16":
            raise ValueError(
                "O formato de áudio precisa ser int16."
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
    def dtype(self) -> str:
        return self._dtype

    @property
    def device(self) -> int | str | None:
        return self._device

    async def capture(
        self,
        duration_seconds: float = 5.0,
    ) -> CapturedAudio:
        return await asyncio.to_thread(
            self.capture_sync,
            duration_seconds,
        )

    def capture_sync(
        self,
        duration_seconds: float = 5.0,
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
                "Não foi possível capturar o áudio do microfone."
            ) from error

        try:
            audio_data = recording.tobytes()

        except Exception as error:
            raise AudioCaptureError(
                "Não foi possível converter o áudio capturado."
            ) from error

        if not audio_data:
            raise AudioCaptureError(
                "Nenhum áudio foi capturado."
            )

        return CapturedAudio(
            data=audio_data,
            sample_rate=self._sample_rate,
            channels=self._channels,
            sample_width=2,
            duration_seconds=duration_seconds,
        )

    def list_devices(
        self,
    ) -> list[dict[str, Any]]:
        sounddevice = self._load_sounddevice()

        try:
            devices = sounddevice.query_devices()

        except Exception as error:
            raise AudioCaptureError(
                "Não foi possível listar os dispositivos de áudio."
            ) from error

        return [
            {
                "index": index,
                "name": str(device.get("name", "")),
                "input_channels": int(
                    device.get(
                        "max_input_channels",
                        0,
                    )
                ),
                "output_channels": int(
                    device.get(
                        "max_output_channels",
                        0,
                    )
                ),
                "default_sample_rate": float(
                    device.get(
                        "default_samplerate",
                        0.0,
                    )
                ),
            }
            for index, device in enumerate(devices)
        ]

    def _load_sounddevice(
        self,
    ) -> Any:
        try:
            import sounddevice

        except ImportError as error:
            raise AudioCaptureError(
                "A biblioteca sounddevice não está instalada."
            ) from error

        return sounddevice
