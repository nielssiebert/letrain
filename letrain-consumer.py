#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import signal
import sys
from dataclasses import dataclass

import paho.mqtt.client as mqtt

try:
    import RPi.GPIO as GPIO
except ImportError:  # pragma: no cover - only used on non-RPi hosts
    GPIO = None


LOGGER = logging.getLogger("letrain-consumer")


@dataclass(frozen=True)
class Settings:
    mqtt_host: str
    mqtt_port: int
    mqtt_topic: str
    mqtt_qos: int
    relay_active_low: bool
    default_pin: int | None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            mqtt_host=os.getenv("MQTT_HOST", "127.0.0.1"),
            mqtt_port=_parse_int("MQTT_PORT", 1883),
            mqtt_topic=os.getenv("MQTT_TOPIC", "tima/execution-events"),
            mqtt_qos=_parse_int("MQTT_QOS", 1),
            relay_active_low=_parse_bool("RELAY_ACTIVE_LOW", False),
            default_pin=_parse_optional_int("LETRAIN_DEFAULT_PIN"),
        )


class RelayController:
    def __init__(self, active_low: bool) -> None:
        self._active_low = active_low
        self._gpio_enabled = GPIO is not None
        self._initialized = False
        self._configured_pins: set[int] = set()

    def set_pin_state(self, pin: int, enabled: bool) -> None:
        self._initialize_gpio()
        on_value, off_value = self._on_off_values()
        target_value = on_value if enabled else off_value

        if not self._gpio_enabled:
            LOGGER.info("Dry run: pin %s -> %s", pin, enabled)
            return

        self._setup_pin_if_needed(pin, off_value)
        GPIO.output(pin, target_value)
        LOGGER.info("Pin %s -> %s", pin, enabled)

    def cleanup(self) -> None:
        if self._gpio_enabled and self._initialized:
            GPIO.cleanup()
            self._initialized = False

    def _initialize_gpio(self) -> None:
        if self._initialized:
            return
        if not self._gpio_enabled:
            LOGGER.warning("RPi.GPIO not available; running in dry-run mode")
            self._initialized = True
            return
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self._initialized = True

    def _setup_pin_if_needed(self, pin: int, initial_value: int) -> None:
        if pin in self._configured_pins:
            return
        GPIO.setup(pin, GPIO.OUT, initial=initial_value)
        self._configured_pins.add(pin)

    def _on_off_values(self) -> tuple[int, int]:
        if self._active_low:
            return GPIO.LOW, GPIO.HIGH
        return GPIO.HIGH, GPIO.LOW


def _parse_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def _parse_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        LOGGER.warning("Invalid integer for %s=%s; using default %s", name, value, default)
        return default


def _parse_optional_int(name: str) -> int | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        LOGGER.warning("Invalid integer for %s=%s; ignoring", name, value)
        return None


def _parse_pin(payload: dict, fallback_pin: int | None) -> int | None:
    pin = payload.get("pin", fallback_pin)
    if pin is None:
        return None
    try:
        return int(pin)
    except (TypeError, ValueError):
        LOGGER.warning("Invalid pin value in payload: %s", pin)
        return None


def _build_on_message(settings: Settings, relay_controller: RelayController):
    def on_message(_client, _userdata, msg) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            LOGGER.warning("Ignoring invalid JSON payload")
            return

        action = str(payload.get("action", "")).upper()
        if action not in {"START", "STOP"}:
            return

        pin = _parse_pin(payload, settings.default_pin)
        if pin is None:
            LOGGER.warning("No pin configured in payload and no default pin set")
            return

        relay_controller.set_pin_state(pin, action == "START")

    return on_message


def _register_signals(client: mqtt.Client, relay_controller: RelayController) -> None:
    def handle_signal(_signum, _frame) -> None:
        LOGGER.info("Shutdown signal received")
        try:
            client.disconnect()
        finally:
            relay_controller.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)


def main() -> int:
    logging.basicConfig(
        level=os.getenv("LETRAIN_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = Settings.from_env()
    relay_controller = RelayController(settings.relay_active_low)

    client = mqtt.Client(client_id="letrain-consumer")
    client.on_connect = lambda c, _u, _f, _rc: c.subscribe(settings.mqtt_topic, qos=settings.mqtt_qos)
    client.on_message = _build_on_message(settings, relay_controller)
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    _register_signals(client, relay_controller)

    LOGGER.info("Connecting to MQTT broker %s:%s", settings.mqtt_host, settings.mqtt_port)
    client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
    client.loop_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
