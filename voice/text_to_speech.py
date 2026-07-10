from __future__ import annotations
from pathlib import Path
import tempfile
import edge_tts
from core.ports import SpeechSynthesizer


class TextToSpeech(SpeechSynthesizer):
    def __init__(self, voice: str) -> None:
        self.voice = voice

    async def speak(self, text: str) -> None:
        if not text.strip():
            return
        output = Path(tempfile.gettempdir()) / "zyron_response.mp3"
        communicate = edge_tts.Communicate(text=text, voice=self.voice)
        await communicate.save(str(output))
