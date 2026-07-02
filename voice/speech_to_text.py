from typing import Any
from faster_whisper import WhisperModel


class SpeechToText:

    def __init__(self, model_name: str, language: str) -> None:
        self.model_name = model_name
        self.language = language
        self._model: WhisperModel | None = None

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        return self._model

    def listen_once(self) -> Any:
        """Captura um comando de áudio do microfone. 
        Este placeholder de MVP retorna `None` até que um backend de microfone seja conectado.
        Versões futuras poderão integrar `sounddevice`, `pyaudio` ou uma API de áudio do Windows.
        """
        return None

    def transcribe(self, audio: Any) -> str:
        if audio is None:
            return ""
        segments, _ = self.model.transcribe(audio, language=self.language[:2])
        return " ".join(segment.text.strip() for segment in segments).strip()
