import requests


class WeatherService:

    def __init__(self, api_key: str, city: str) -> None:
        self.api_key = api_key
        self.city = city

    def current_temperature_text(self) -> str:
        if not self.api_key:
            return "indisponível"
        params = {"q": self.city, "appid": self.api_key, "units": "metric", "lang": "pt_br"}
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=15)
        response.raise_for_status()
        temp = round(response.json()["main"]["temp"])
        return f"{temp} graus"
