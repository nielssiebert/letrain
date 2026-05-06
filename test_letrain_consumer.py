import importlib.util
import json
import os
import pathlib
import sys
import types
import unittest
from unittest.mock import patch


MODULE_PATH = pathlib.Path(__file__).resolve().parent / "letrain-consumer.py"


class _FakeGpioModule:
    BCM = "BCM"
    OUT = "OUT"
    HIGH = 1
    LOW = 0

    def __init__(self) -> None:
        self.setup_calls: list[tuple[int, str, int]] = []
        self.output_calls: list[tuple[int, int]] = []
        self.mode_calls: list[str] = []
        self.cleanup_called = False

    def setwarnings(self, _enabled: bool) -> None:
        return None

    def setmode(self, mode: str) -> None:
        self.mode_calls.append(mode)

    def setup(self, pin: int, mode: str, initial: int) -> None:
        self.setup_calls.append((pin, mode, initial))

    def output(self, pin: int, value: int) -> None:
        self.output_calls.append((pin, value))

    def cleanup(self) -> None:
        self.cleanup_called = True


if "paho.mqtt.client" not in sys.modules:
    paho_module = types.ModuleType("paho")
    mqtt_module = types.ModuleType("paho.mqtt")
    client_module = types.ModuleType("paho.mqtt.client")
    client_module.Client = object
    mqtt_module.client = client_module
    paho_module.mqtt = mqtt_module
    sys.modules["paho"] = paho_module
    sys.modules["paho.mqtt"] = mqtt_module
    sys.modules["paho.mqtt.client"] = client_module


SPEC = importlib.util.spec_from_file_location("letrain_consumer", MODULE_PATH)
letrain_consumer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = letrain_consumer
SPEC.loader.exec_module(letrain_consumer)


class ConsumerTests(unittest.TestCase):
    def test_settings_from_env_uses_default_allowed_pins(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = letrain_consumer.Settings.from_env()

        self.assertEqual(settings.allowed_pins, (16, 19, 20, 26))

    def test_settings_from_env_parses_allowed_pins_csv(self):
        with patch.dict(
            os.environ,
            {"LETRAIN_ALLOWED_PINS": "26, 20, 26, 19", "LETRAIN_DEFAULT_PIN": "20"},
            clear=True,
        ):
            settings = letrain_consumer.Settings.from_env()

        self.assertEqual(settings.allowed_pins, (26, 20, 19))
        self.assertEqual(settings.default_pin, 20)

    def test_initialize_pins_sets_up_all_allowed_pins_once(self):
        fake_gpio = _FakeGpioModule()

        with patch.object(letrain_consumer, "GPIO", fake_gpio):
            controller = letrain_consumer.RelayController(active_low=False, allowed_pins=(26, 16, 20))
            controller.initialize_pins()

        self.assertEqual(fake_gpio.mode_calls, [fake_gpio.BCM])
        self.assertEqual(
            fake_gpio.setup_calls,
            [
                (16, fake_gpio.OUT, fake_gpio.LOW),
                (20, fake_gpio.OUT, fake_gpio.LOW),
                (26, fake_gpio.OUT, fake_gpio.LOW),
            ],
        )

    def test_set_pin_state_ignores_disallowed_pin(self):
        fake_gpio = _FakeGpioModule()

        with patch.object(letrain_consumer, "GPIO", fake_gpio):
            controller = letrain_consumer.RelayController(active_low=False, allowed_pins=(16, 19))
            controller.set_pin_state(20, True)

        self.assertEqual(fake_gpio.setup_calls, [])
        self.assertEqual(fake_gpio.output_calls, [])

    def test_on_message_uses_default_pin_when_whitelisted(self):
        handled: list[tuple[int, bool]] = []

        class _Controller:
            def set_pin_state(self, pin: int, enabled: bool) -> None:
                handled.append((pin, enabled))

        settings = letrain_consumer.Settings(
            mqtt_host="127.0.0.1",
            mqtt_port=1883,
            mqtt_topic="tima/execution-events",
            mqtt_qos=1,
            relay_active_low=False,
            allowed_pins=(16, 19, 20, 26),
            default_pin=19,
        )
        message = types.SimpleNamespace(payload=json.dumps({"action": "START"}).encode("utf-8"))

        letrain_consumer._build_on_message(settings, _Controller())(None, None, message)

        self.assertEqual(handled, [(19, True)])


if __name__ == "__main__":
    unittest.main()