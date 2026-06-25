"""
ROADMAP DO MÓDULO

Versão Atual:

* Gera áudio MP3 com Edge-TTS.

Próxima Versão:

* Adicionar reprodução real, seleção dinâmica de voz e cache.

Versão Futura:

* Vozes personalizadas, emoção na fala e fallback offline.

Dependências Futuras:

* Edge-TTS, Piper/Coqui, cache local
"""

# TODO:
# Implementar reprodução automática do áudio gerado e testes com mock do Edge-TTS.
# FIXME:
# O módulo salva MP3 temporário, mas ainda não toca a resposta para o usuário.
# IMPROVEMENT:
# Permitir escolha dinâmica de voz, velocidade, volume, idioma e fallback offline.
# FUTURE:
# Integrar vozes locais como Piper/Coqui, emoção na fala e perfis vocais por usuário.
# OPTIMIZATION:
# Cachear frases frequentes como saudação e confirmações curtas para reduzir latência.
# SECURITY:
# Limpar arquivos temporários e evitar sintetizar conteúdo sensível em ambientes públicos sem confirmação.


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
