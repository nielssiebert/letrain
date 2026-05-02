#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import signal
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from threading import Event
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import paho.mqtt.client as mqtt


LOGGER = logging.getLogger("letrain-weather-factor")


@dataclass(frozen=True)
class Settings:
    mqtt_host: str
    mqtt_port: int
    mqtt_topic: str
    mqtt_qos: int
    factor_id: str
    latitude: float
    longitude: float
    timezone: str
    api_base_url: str
    request_timeout_seconds: int
    publish_interval_seconds: int
    rain_full_scale_mm: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            mqtt_host=os.getenv("MQTT_HOST", "127.0.0.1"),
            mqtt_port=_parse_int("MQTT_PORT", 1883),
            mqtt_topic=os.getenv("MQTT_TOPIC", "tima/factors/values"),
            mqtt_qos=_parse_int("MQTT_QOS", 1),
            factor_id=os.getenv("FACTOR_ID", "weather_forecast"),
            latitude=_parse_float("WEATHER_LATITUDE", 52.52),
            longitude=_parse_float("WEATHER_LONGITUDE", 13.405),
            timezone=os.getenv("WEATHER_TIMEZONE", "auto"),
            api_base_url=os.getenv("WEATHER_API_BASE_URL", "https://api.open-meteo.com/v1/forecast"),
            request_timeout_seconds=_parse_int("WEATHER_REQUEST_TIMEOUT_SECONDS", 20),
            publish_interval_seconds=_parse_int("WEATHER_PUBLISH_INTERVAL_SECONDS", 21600),
            rain_full_scale_mm=_parse_float("WEATHER_RAIN_FULL_SCALE_MM", 20.0),
        )


def _parse_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        LOGGER.warning("Invalid integer for %s=%s; using default %s", name, value, default)
        return default


def _parse_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        LOGGER.warning("Invalid float for %s=%s; using default %s", name, value, default)
        return default


def _build_weather_url(settings: Settings) -> str:
    params = {
        "latitude": settings.latitude,
        "longitude": settings.longitude,
        "timezone": settings.timezone,
        "daily": "precipitation_sum",
        "forecast_days": 1,
    }
    return f"{settings.api_base_url}?{urlencode(params)}"


def _fetch_today_rain_mm(settings: Settings) -> float:
    url = _build_weather_url(settings)
    request = Request(url, headers={"User-Agent": "letrain-weather-factor/1.0"})
    try:
        with urlopen(request, timeout=settings.request_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Weather request failed: {exc}") from exc

    daily = payload.get("daily") or {}
    precipitation = daily.get("precipitation_sum") or []
    if not precipitation:
        raise RuntimeError("Weather response missing daily precipitation_sum")
    return max(float(precipitation[0]), 0.0)


def _compute_factor_value(rain_mm: float, full_scale_mm: float) -> float:
    if full_scale_mm <= 0:
        return 0.0
    capped_rain = min(max(rain_mm, 0.0), full_scale_mm)
    ratio = capped_rain / full_scale_mm
    factor = 1.0 - ratio
    return round(min(max(factor, 0.0), 1.0), 3)


def _build_factor_payload(settings: Settings, rain_mm: float, factor_value: float) -> dict:
    return {
        "message_id": str(uuid.uuid4()),
        "current_timestamp": datetime.now().astimezone().isoformat(),
        "factor_id": settings.factor_id,
        "value": factor_value,
        "rain_mm_today": round(rain_mm, 2),
        "source": "open-meteo",
    }


def _publish_factor(settings: Settings, payload: dict) -> None:
    client = mqtt.Client(client_id="letrain-weather-factor")
    client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
    info = client.publish(settings.mqtt_topic, json.dumps(payload), qos=settings.mqtt_qos)
    info.wait_for_publish()
    client.disconnect()


def _publish_current_weather_factor(settings: Settings) -> None:
    rain_mm = _fetch_today_rain_mm(settings)
    factor_value = _compute_factor_value(rain_mm, settings.rain_full_scale_mm)
    payload = _build_factor_payload(settings, rain_mm, factor_value)
    _publish_factor(settings, payload)
    LOGGER.info(
        "Published factor %s value=%s rain_mm_today=%s",
        settings.factor_id,
        factor_value,
        round(rain_mm, 2),
    )


def _register_signals(stop_event: Event) -> None:
    def handle_signal(_signum, _frame) -> None:
        LOGGER.info("Shutdown signal received")
        stop_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)


def main() -> int:
    logging.basicConfig(
        level=os.getenv("LETRAIN_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = Settings.from_env()
    stop_event = Event()
    _register_signals(stop_event)

    while not stop_event.is_set():
        try:
            _publish_current_weather_factor(settings)
        except Exception as exc:  # pragma: no cover - runtime guard
            LOGGER.error("Weather factor publish failed: %s", exc)
        stop_event.wait(settings.publish_interval_seconds)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
