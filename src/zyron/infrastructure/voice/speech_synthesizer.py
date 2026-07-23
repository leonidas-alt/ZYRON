from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any

from zyron.infrastructure.voice.exceptions import SpeechSynthesisError


class SpeechSynthesizer:
    def __init__(
        self,
        voice_name: str = "pt-BR-FranciscaNeural",
        rate: int = 0,
        volume: int = 100,
    ) -> None:
        if not voice_name.strip():
            raise ValueError(
                "O nome da voz não pode estar vazio."
            )

        if rate < -100 or rate > 100:
            raise ValueError(
                "A velocidade da voz deve estar entre -100 e 100."
            )

        if volume < 0 or volume > 100:
            raise ValueError(
                "O volume da voz deve estar entre 0 e 100."
            )

        self._voice_name = voice_name.strip()
        self._rate = rate
        self._volume = volume

    @property
    def voice_name(self) -> str:
        return self._voice_name

    @property
    def rate(self) -> int:
        return self._rate

    @property
    def volume(self) -> int:
        return self._volume

    async def speak(
        self,
        text: str,
    ) -> None:
        normalized_text = text.strip()

        if not normalized_text:
            return

        audio_path = await self.synthesize(
            normalized_text
        )

        try:
            await asyncio.to_thread(
                self._play_audio,
                audio_path,
            )
        finally:
            audio_path.unlink(
                missing_ok=True
            )

    async def synthesize(
        self,
        text: str,
        output_path: str | Path | None = None,
    ) -> Path:
        normalized_text = text.strip()

        if not normalized_text:
            raise SpeechSynthesisError(
                "O texto para síntese não pode estar vazio."
            )

        destination = self._resolve_output_path(
            output_path
        )

        edge_tts = self._load_edge_tts()

        try:
            communicator = edge_tts.Communicate(
                text=normalized_text,
                voice=self._voice_name,
                rate=self._format_rate(),
                volume=self._format_volume(),
            )

            await communicator.save(
                str(destination)
            )

        except Exception as error:
            destination.unlink(
                missing_ok=True
            )

            raise SpeechSynthesisError(
                "Não foi possível gerar o áudio da fala."
            ) from error

        if not destination.exists():
            raise SpeechSynthesisError(
                "O arquivo de áudio não foi gerado."
            )

        return destination

    def speak_sync(
        self,
        text: str,
    ) -> None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(
                self.speak(text)
            )
            return

        raise SpeechSynthesisError(
            "O método speak_sync não pode ser executado "
            "dentro de um loop assíncrono ativo."
        )

    def _play_audio(
        self,
        audio_path: Path,
    ) -> None:
        pygame = self._load_pygame()

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.music.load(
                str(audio_path)
            )

            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(20)

            pygame.mixer.music.unload()

        except Exception as error:
            raise SpeechSynthesisError(
                "Não foi possível reproduzir o áudio da fala."
            ) from error

    def _resolve_output_path(
        self,
        output_path: str | Path | None,
    ) -> Path:
        if output_path is not None:
            destination = Path(
                output_path
            ).expanduser()

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            return destination

        temporary_file = tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False,
        )

        temporary_path = Path(
            temporary_file.name
        )

        temporary_file.close()

        return temporary_path

    def _format_rate(self) -> str:
        return f"{self._rate:+d}%"

    def _format_volume(self) -> str:
        volume_difference = self._volume - 100

        return f"{volume_difference:+d}%"

    def _load_edge_tts(
        self,
    ) -> Any:
        try:
            import edge_tts

        except ImportError as error:
            raise SpeechSynthesisError(
                "A biblioteca edge-tts não está instalada."
            ) from error

        return edge_tts

    def _load_pygame(
        self,
    ) -> Any:
        try:
            import pygame

        except ImportError as error:
            raise SpeechSynthesisError(
                "A biblioteca pygame não está instalada."
            ) from error

        return pygame
