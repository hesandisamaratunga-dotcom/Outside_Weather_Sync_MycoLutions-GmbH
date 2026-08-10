"""
Fetches current outside temperature and humidity for Helvesiek, Lower Saxony,
from Open-Meteo
(free, no API key required) and pushes it to Datacake.

Reuses secrets already set up for the substrate script:
  DATACAKE_TOKEN
  DATACAKE_DEVICE_ID
"""

import os
import sys
import requests

# ---------- Configuration ----------
LATITUDE = 53.2144    # Helvesiek, Lower Saxony
LONGITUDE = 9.4931
TEMPERATURE_FIELD = "OUTSIDE_TEMPERATURE"
HUMIDITY_FIELD = "OUTSIDE_HUMIDITY"

DATACAKE_TOKEN = os.environ["DATACAKE_TOKEN"]
DATACAKE_DEVICE_ID = os.environ["DATACAKE_DEVICE_ID"]


def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,relative_humidity_2m",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    current = resp.json()["current"]
    return current["temperature_2m"], current["relative_humidity_2m"]


def push_to_datacake(temperature, humidity):
    url = f"https://api.datacake.co/v1/devices/{DATACAKE_DEVICE_ID}/record/?batch=true"
    headers = {
        "Authorization": f"Token {DATACAKE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = [
        {"field": TEMPERATURE_FIELD, "value": temperature},
        {"field": HUMIDITY_FIELD, "value": humidity},
    ]
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


def main():
    print("Fetching outside weather for Helvesiek...")
    temperature, humidity = get_weather()
    print(f"Outside temperature: {temperature} C, humidity: {humidity} %")

    print("Pushing to Datacake...")
    result = push_to_datacake(temperature, humidity)
    print("Datacake response:", result)


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Missing required environment variable: {e}", file=sys.stderr)
        sys.exit(1)
