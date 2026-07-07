from __future__ import annotations
import asyncio
from typing import Any
import requests
from core.ports import WeatherProvider


class WeatherService(WeatherProvider):

    def __init__(self, api_key: str, city: str, timeout: int = 15) -> None:
        self.api_key = api_key
        self.city = city
        self.timeout = timeout

    async def current_temperature_text(self) -> str:
        if not self.api_key:
            return "indisponível"

        params = {"q": self.city, "appid": self.api_key, "units": "metric", "lang": "pt_br"}
        try:
            response = await asyncio.to_thread(
                requests.get,
                "https://api.openweathermap.org/data/2.5/weather",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            temp = round(float(data["main"]["temp"]))
            return f"{temp} graus"
        except requests.Timeout:
            return "indisponível por timeout"
        except requests.ConnectionError:
            return "indisponível por falha de conexão"
        except requests.HTTPError:
            return "indisponível no provedor de clima"
        except (KeyError, TypeError, ValueError, requests.JSONDecodeError):
            return "indisponível por resposta inválida"
