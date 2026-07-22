from __future__ import annotations


class VoiceError(Exception):
    pass


class SpeechSynthesisError(VoiceError):
    pass


class SpeechRecognitionError(VoiceError):
    pass


class AudioCaptureError(VoiceError):
    pass


class WakeWordDetectionError(VoiceError):
    pass
