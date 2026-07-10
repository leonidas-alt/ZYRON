class VoiceError(Exception):
    """Base error for voice infrastructure failures."""


class MicrophoneUnavailableError(VoiceError):
    """Raised when the microphone cannot be opened or used."""


class AudioCaptureError(VoiceError):
    """Raised when audio capture fails after the device is available."""


class TranscriptionError(VoiceError):
    """Raised when speech transcription fails."""


class SpeechSynthesisError(VoiceError):
    """Raised when speech synthesis or playback fails."""


class WakeWordError(VoiceError):
    """Raised when wake-word processing fails."""
