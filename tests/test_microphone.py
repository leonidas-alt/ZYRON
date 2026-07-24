from __future__ import annotations

import sounddevice as sd
import soundfile as sf


SAMPLE_RATE = 16000
DURATION_SECONDS = 5
OUTPUT_FILE = "microphone_test.wav"


print("Gravando por 5 segundos...")

audio = sd.rec(
    int(DURATION_SECONDS * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    device=1,
)

sd.wait()

sf.write(
    OUTPUT_FILE,
    audio,
    SAMPLE_RATE,
)

print(f"Áudio salvo em {OUTPUT_FILE}")