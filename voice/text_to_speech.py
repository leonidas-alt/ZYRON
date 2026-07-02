import asyncio
import tempfile
from pathlib import Path
import edge_tts


class TextToSpeech:

    def __init__(self, voice: str) -> None:
        self.voice = voice

    def speak(self, text: str) -> None:
        if not text.strip():
            return
        asyncio.run(self._speak_async(text))

    async def _speak_async(self, text: str) -> None:
        output = Path(tempfile.gettempdir()) / "zyron_response.mp3"
        communicate = edge_tts.Communicate(text=text, voice=self.voice)
        await communicate.save(str(output))
