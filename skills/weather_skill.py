"""
Aara Weather Skill
Get weather information using Open-Meteo (free) or OpenWeatherMap.
"""

import logging
from typing import List, Optional

import requests

from skills.base_skill import BaseSkill
from config.settings import SETTINGS, WeatherProvider

logger = logging.getLogger(__name__)


class WeatherSkill(BaseSkill):
    """Provides weather information."""

    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Get current weather for any city"

    @property
    def keywords(self) -> List[str]:
        return ["weather", "temperature", "forecast", "rain", "sunny", "cold", "hot"]

    def __init__(self):
        """Initialize weather skill."""
        self._provider = SETTINGS.weather.provider
        self._api_key = SETTINGS.weather.openweathermap_key
        self._default_city = SETTINGS.weather.default_city

    def execute(self, params: dict) -> str:
        """
        Get weather for a city.

        Args:
            params: {"city": "city name"}

        Returns:
            Weather description
        """
        city = params.get("city", self._default_city)

        if self._provider == WeatherProvider.OPENWEATHERMAP and self._api_key:
            return self._get_openweathermap(city)
        else:
            return self._get_open_meteo(city)

    def _get_open_meteo(self, city: str) -> str:
        """Get weather from Open-Meteo (free, no API key)."""
        try:
            # First, get coordinates for the city
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_response = requests.get(geo_url, timeout=10)
            geo_data = geo_response.json()

            if not geo_data.get("results"):
                return f"I couldn't find weather data for '{city}'."

            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            city_name = location.get("name", city)
            country = location.get("country", "")

            # Get weather data
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current_weather=true"
                f"&hourly=temperature_2m,relative_humidity_2m"
            )
            weather_response = requests.get(weather_url, timeout=10)
            weather_data = weather_response.json()

            current = weather_data.get("current_weather", {})
            temp = current.get("temperature", "N/A")
            windspeed = current.get("windspeed", 0)
            weather_code = current.get("weathercode", 0)

            # Decode weather code
            weather_desc = self._decode_weather_code(weather_code)

            # Build response
            response = (
                f"In {city_name}, {country}, it's currently {temp}°C and {weather_desc}. "
                f"Wind speed is {windspeed} km/h."
            )

            if temp is not None:
                if float(temp) > 30:
                    response += " It's quite hot, stay hydrated!"
                elif float(temp) < 10:
                    response += " It's chilly, dress warmly!"

            return response

        except Exception as e:
            logger.error(f"Open-Meteo error: {e}")
            return f"I couldn't get the weather for {city}. Try again later?"

    def _get_openweathermap(self, city: str) -> str:
        """Get weather from OpenWeatherMap API."""
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={self._api_key}&units=metric"
            )
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get("cod") != 200:
                return f"I couldn't find weather data for '{city}'."

            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})

            temp = main.get("temp", "N/A")
            feels_like = main.get("feels_like", "N/A")
            humidity = main.get("humidity", "N/A")
            description = weather.get("description", "").capitalize()
            windspeed = wind.get("speed", 0)

            city_name = data.get("name", city)
            country = data.get("sys", {}).get("country", "")

            response = (
                f"In {city_name}, {country}, it's {temp}°C (feels like {feels_like}°C) "
                f"and {description}. Humidity is {humidity}%, wind speed {windspeed} m/s."
            )

            return response

        except Exception as e:
            logger.error(f"OpenWeatherMap error: {e}")
            # Fall back to Open-Meteo
            return self._get_open_meteo(city)

    def _decode_weather_code(self, code: int) -> str:
        """Decode Open-Meteo weather code to description."""
        codes = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "foggy",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            73: "moderate snow",
            75: "heavy snow",
            77: "snow grains",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "slight snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
            96: "thunderstorm with hail",
            99: "thunderstorm with heavy hail",
        }
        return codes.get(code, "unknown conditions")
