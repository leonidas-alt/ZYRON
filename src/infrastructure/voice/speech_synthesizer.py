from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from uuid import uuid4

from src.ai.application.ports import SpeechSynthesizerPort
from infrastructure.voice.exceptions import SpeechSynthesisError


class EdgeSpeechSynthesizer(SpeechSynthesizerPort):
    def __init__(self, voice: str = "pt-BR-AntonioNeural", rate: str = "+0%", volume: str = "+0%") -> None:
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self._lock = asyncio.Lock()

    async def speak(self, text: str) -> None:
        if not text.strip():
            return
        async with self._lock:
            await self._speak_locked(text)

    async def _speak_locked(self, text: str) -> None:
        output = Path(tempfile.gettempdir()) / f"zyron_tts_{uuid4().hex}.mp3"
        try:
            import edge_tts

            communicate = edge_tts.Communicate(text=text, voice=self.voice, rate=self.rate, volume=self.volume)
            await communicate.save(str(output))
            await asyncio.to_thread(self._play_audio, output)
        except Exception as exc:
            raise SpeechSynthesisError("Falha ao sintetizar ou reproduzir a resposta de voz.") from exc
        finally:
            try:
                output.unlink(missing_ok=True)
            except Exception:
                pass

    def _play_audio(self, output: Path) -> None:
        try:
            import pygame

            pygame.mixer.init()
            pygame.mixer.music.load(str(output))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(20)
            pygame.mixer.music.unload()
            pygame.mixer.quit()
        except Exception as exc:
            raise SpeechSynthesisError("Falha ao reproduzir o áudio sintetizado.") from exc
