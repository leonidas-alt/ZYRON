from __future__ import annotations


class VoiceError(Exception):
    pass


class AudioCaptureError(VoiceError):
    pass


class SpeechRecognitionError(VoiceError):
    pass


class SpeechSynthesisError(VoiceError):
    pass


class WakeWordDetectionError(VoiceError):
    pass
