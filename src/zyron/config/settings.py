from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    assistant_name: str
    owner_name: str

    zyron_ollama_base_url: str
    zyron_ollama_model: str
    zyron_ollama_timeout_seconds: float

    database_path: Path

   voice_enabled: bool
    voice_rate: int
    voice_volume: float
    voice_name: str | None

    audio_sample_rate: int
    audio_channels: int
    audio_dtype: str
    audio_device: int | str |None
    recording_duration_seconds: float

    whisper_model: str
    whisper_device: str
    whisper_compute_type: str
    whisper_language: str | None
    whisper_beam_size: int
    whisper_vad_filter: bool
    wake_words: tuple[str, ...]

    @classmethod
    def from_env(cls) -> Settings:
        settings = cls(
            assistant_name=_get_string(
                "ZYRON_ASSISTANT_NAME",
                default="ZYRON",
            ),
            owner_name=_get_string(
                "ZYRON_OWNER_NAME",
                default="Usuário",
            ),
            ollama_base_url=_get_string(
                "ZYRON_OLLAMA_BASE_URL",
                default="http://localhost:11434",
            ),
            ollama_model=_get_string(
                "ZYRON_OLLAMA_MODEL",
                default="llama3.2",
            ),
            ollama_timeout_seconds=_get_float(
                "ZYRON_OLLAMA_TIMEOUT_SECONDS",
                default=120.0,
                minimum=1.0,
            ),
            database_path=Path(
                _get_string(
                    "ZYRON_DATABASE_PATH",
                    default="data/zyron.db",
                )
            ),
            voice_enabled=_get_bool(
                "ZYRON_VOICE_ENABLED",
                default=True,
            ),
            voice_rate=_get_int(
                "ZYRON_VOICE_RATE",
                default=180,
                minimum=1,
            ),
            voice_volume=_get_float(
                "ZYRON_VOICE_VOLUME",
                default=1.0,
                minimum=0.0,
                maximum=1.0,
            ),
            voice_name=_get_optional_string(
                "ZYRON_VOICE_NAME",
            ),
            audio_sample_rate=_get_int(
                "ZYRON_AUDIO_SAMPLE_RATE",
                default=16_000,
                minimum=1,
            ),
            audio_channels=_get_int(
                "ZYRON_AUDIO_CHANNELS",
                default=1,
                minimum=1,
            ),
            audio_dtype=_get_string(
                "ZYRON_AUDIO_DTYPE",
                default="int16",
            ),
            audio_device=_get_audio_device(
                "ZYRON_AUDIO_DEVICE",
            ),
            recording_duration_seconds=_get_float(
                "ZYRON_RECORDING_DURATION_SECONDS",
                default=5.0,
                minimum=0.1,
            ),
            whisper_model=_get_string(
            "ZYRON_WHISPER_MODEL",
            default="small",
            ),

            whisper_device=_get_string(
                "ZYRON_WHISPER_DEVICE",
                default="cpu",
            ),
            
            whisper_compute_type=_get_string(
                "ZYRON_WHISPER_COMPUTE_TYPE",
                default="int8",
            ),
            
            whisper_language=_get_optional_string(
                "ZYRON_WHISPER_LANGUAGE",
                default="pt",
            ),

            whisper_beam_size=_get_int(
                "ZYRON_WHISPER_BEAM_SIZE",
                default=5,
                minimum=1,
            ),
            
            whisper_vad_filter=_get_bool(
                "ZYRON_WHISPER_VAD_FILTER",
                default=True,
            ),,
            wake_words=_get_csv_tuple(
                "ZYRON_WAKE_WORDS",
                default=(
                    "zyron",
                    "ziron",
                    "sairon",
                ),
            ),
        )

        settings.validate()

        return settings

    def validate(self) -> None:
        if self.audio_sample_rate != 16000:
    raise ValueError(
        "O Faster Whisper exige áudio em 16 kHz."
    )

        if self.audio_channels != 1:
            raise ValueError(
                "O Faster Whisper exige áudio mono."
            )
        
        if self.audio_dtype != "int16":
            raise ValueError(
                "O Faster Whisper exige áudio int16."
            )
        
        if self.whisper_beam_size <= 0:
            raise ValueError(
                "Beam size inválido."
            )
        
        if not self.whisper_model.strip():
            raise ValueError(
                "Modelo Whisper inválido."
            )
        
        if not self.whisper_device.strip():
            raise ValueError(
                "Device Whisper inválido."
            )
        
        if not self.whisper_compute_type.strip():
            raise ValueError(
                "Compute type Whisper inválido."
            )
    def _get_string(
        name: str,
        default: str,
    ) -> str:
        value = os.getenv(name)
    
        if value is None:
            return default
    
        cleaned_value = value.strip()
    
        return cleaned_value or default


    def _get_optional_string(
        name: str,
        default: str | None = None,
    ) -> str | None:
    
        value = os.getenv(name)
    
        if value is None:
            return default
    
        value = value.strip()
    
        if value == "":
            return default
    
        return value

    
    def _get_bool(
        name: str,
        default: bool,
    ) -> bool:
        value = os.getenv(name)
    
        if value is None:
            return default
    
        normalized_value = value.strip().casefold()
    
        truthy_values = {
            "1",
            "true",
            "yes",
            "sim",
            "on",
            "enabled",
            "ativado",
        }
    
        falsy_values = {
            "0",
            "false",
            "no",
            "nao",
            "não",
            "off",
            "disabled",
            "desativado",
        }
    
        if normalized_value in truthy_values:
            return True
    
        if normalized_value in falsy_values:
            return False
    
        raise ValueError(
            f"A variável {name} deve representar um valor booleano."
        )
    
    
    def _get_int(
        name: str,
        default: int,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        value = os.getenv(name)
    
        if value is None:
            resolved_value = default
        else:
            try:
                resolved_value = int(value.strip())
            except ValueError as error:
                raise ValueError(
                    f"A variável {name} deve ser um número inteiro."
                ) from error
    
        _validate_numeric_range(
            name=name,
            value=resolved_value,
            minimum=minimum,
            maximum=maximum,
        )
    
        return resolved_value
    
    
    def _get_float(
        name: str,
        default: float,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> float:
        value = os.getenv(name)
    
        if value is None:
            resolved_value = default
        else:
            try:
                resolved_value = float(value.strip())
            except ValueError as error:
                raise ValueError(
                    f"A variável {name} deve ser um número."
                ) from error
    
        _validate_numeric_range(
            name=name,
            value=resolved_value,
            minimum=minimum,
            maximum=maximum,
        )
    
        return resolved_value
    
    
    def _get_csv_tuple(
        name: str,
        default: tuple[str, ...],
    ) -> tuple[str, ...]:
        value = os.getenv(name)
    
        if value is None:
            return default
    
        values = tuple(
            item.strip()
            for item in value.split(",")
            if item.strip()
        )
    
        return values or default
    
    
    def _get_audio_device(
        name: str,
    ) -> int | str | None:
        value = os.getenv(name)
    
        if value is None:
            return None
    
        cleaned_value = value.strip()
    
        if not cleaned_value:
            return None
    
        try:
            return int(cleaned_value)
        except ValueError:
            return cleaned_value
    
    
    def _validate_numeric_range(
        name: str,
        value: int | float,
        minimum: int | float | None,
        maximum: int | float | None,
    ) -> None:
        if minimum is not None and value < minimum:
            raise ValueError(
                f"A variável {name} deve ser maior ou igual a {minimum}."
            )
    
        if maximum is not None and value > maximum:
            raise ValueError(
                f"A variável {name} deve ser menor ou igual a {maximum}."
            )
