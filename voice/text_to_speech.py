"""Text-to-speech synthesis using Microsoft Edge TTS."""

import asyncio
import tempfile
from pathlib import Path
import edge_tts


class TextToSpeech:
    """Converts assistant text responses into spoken audio."""

    def __init__(self, voice: str) -> None:
        """Store the voice identifier used by Edge TTS."""
        self.voice = voice

    def speak(self, text: str) -> None:
        """Synchronously synthesize speech for a text response."""
        if not text.strip():
            return
        asyncio.run(self._speak_async(text))

    async def _speak_async(self, text: str) -> None:
        """Generate an MP3 file; playback integration is planned for the next iteration."""
        output = Path(tempfile.gettempdir()) / "zyron_response.mp3"
        communicate = edge_tts.Communicate(text=text, voice=self.voice)
        await communicate.save(str(output))
