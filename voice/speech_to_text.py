"""
ROADMAP DO MÓDULO

Versão Atual:

* Estrutura transcrição com Faster-Whisper e placeholder de captura.

Próxima Versão:

* Integrar microfone real, VAD e testes com fixtures de áudio.

Versão Futura:

* Streaming contínuo, diarização, reconhecimento facial/voz e perfis.

Dependências Futuras:

* WASAPI, sounddevice, Faster-Whisper, modelos biométricos
"""

# TODO:
# Implementar captura real de microfone no Windows com testes usando fixtures de áudio.
# FIXME:
# listen_once retorna None, então o assistente ainda não recebe voz real em runtime.
# IMPROVEMENT:
# Adicionar VAD, calibração de ruído, seleção de dispositivo e métricas de confiança da transcrição.
# FUTURE:
# Suportar streaming contínuo, diarização, identificação de locutor e reconhecimento facial/voz para multiusuário.
# OPTIMIZATION:
# Manter o modelo carregado e processar áudio em chunks para reduzir latência.
# SECURITY:
# Evitar salvar áudio bruto sem consentimento explícito e política de retenção configurável.


"""Speech recognition using Faster-Whisper."""

from typing import Any
from faster_whisper import WhisperModel


class SpeechToText:
    """Captures microphone audio and converts speech into text."""

    def __init__(self, model_name: str, language: str) -> None:
        """Load the Faster-Whisper model configuration."""
        self.model_name = model_name
        self.language = language
        self._model: WhisperModel | None = None

    @property
    def model(self) -> WhisperModel:
        """Lazily load the Whisper model to speed up object construction."""
        if self._model is None:
            self._model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        return self._model

    def listen_once(self) -> Any:
        """Capture one audio command from the microphone.

        This MVP placeholder returns None until a microphone backend is connected.
        Future versions can integrate sounddevice, pyaudio or a Windows audio API.
        """
        return None

    def transcribe(self, audio: Any) -> str:
        """Transcribe an audio file/path/buffer into normalized text."""
        if audio is None:
            return ""
        segments, _ = self.model.transcribe(audio, language=self.language[:2])
        return " ".join(segment.text.strip() for segment in segments).strip()
