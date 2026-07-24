from __future__ import annotations

from faster_whisper import WhisperModel


AUDIO_FILE = "microphone_test.wav"


model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
)

segments, info = model.transcribe(
    AUDIO_FILE,
    language="pt",
    vad_filter=True,
)

transcription = " ".join(
    segment.text.strip()
    for segment in segments
).strip()

print(f"Idioma detectado: {info.language}")
print(f"Transcrição: {transcription}")