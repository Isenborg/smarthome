"""Weather from Open-Meteo (free, no API key)."""

import json
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen

URL = "https://api.open-meteo.com/v1/forecast"


def fetch(location):
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timezone": location["timezone"],
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,is_day",
        "hourly": "temperature_2m,weather_code,precipitation_probability,is_day",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
        "precipitation_probability_max,sunrise,sunset",
        "wind_speed_unit": "ms",
        "forecast_days": 6,
    }
    with urlopen(f"{URL}?{urlencode(params)}", timeout=20) as resp:
        data = json.load(resp)

    cur = data["current"]
    now_hour = cur["time"][:13]  # "2026-10-29T21"
    h = data["hourly"]
    first = next(i for i, t in enumerate(h["time"]) if t[:13] >= now_hour)
    hourly = [
        {
            "time": h["time"][i][11:16],
            "temp": round(h["temperature_2m"][i]),
            "code": h["weather_code"][i],
            "precip": h["precipitation_probability"][i],
            "is_day": h["is_day"][i],
        }
        for i in range(first + 1, min(first + 13, len(h["time"])))
    ]
    d = data["daily"]
    daily = [
        {
            "date": d["time"][i],
            "code": d["weather_code"][i],
            "max": round(d["temperature_2m_max"][i]),
            "min": round(d["temperature_2m_min"][i]),
            "precip": d["precipitation_probability_max"][i],
            "sunrise": d["sunrise"][i][11:16],
            "sunset": d["sunset"][i][11:16],
        }
        for i in range(len(d["time"]))
    ]
    return {
        "location": location["name"],
        "current": {
            "temp": round(cur["temperature_2m"]),
            "feels": round(cur["apparent_temperature"]),
            "code": cur["weather_code"],
            "wind": round(cur["wind_speed_10m"]),
            "is_day": cur["is_day"],
        },
        "hourly": hourly,
        "daily": daily,
        "updated": datetime.now().isoformat(timespec="seconds"),
    }
