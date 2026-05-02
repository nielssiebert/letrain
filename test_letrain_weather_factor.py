import importlib.util
import json
import os
import pathlib
import sys
import types
import unittest
from urllib.error import URLError
from unittest.mock import patch


MODULE_PATH = pathlib.Path(__file__).resolve().parent / "letrain-weather-factor.py"

# Keep tests self-contained: only weather/factor functions are tested,
# so provide a tiny stub for paho.mqtt used by publish code paths.
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

SPEC = importlib.util.spec_from_file_location("letrain_weather_factor", MODULE_PATH)
weather_factor = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = weather_factor
SPEC.loader.exec_module(weather_factor)


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class WeatherFactorTests(unittest.TestCase):
    def _settings(self, **overrides):
        defaults = {
            "mqtt_host": "127.0.0.1",
            "mqtt_port": 1883,
            "mqtt_topic": "tima/factors/values",
            "mqtt_qos": 1,
            "factor_id": "weather_forecast",
            "latitude": 52.52,
            "longitude": 13.405,
            "timezone": "auto",
            "api_base_url": "https://api.open-meteo.com/v1/forecast",
            "request_timeout_seconds": 20,
            "publish_interval_seconds": 21600,
            "rain_full_scale_mm": 20.0,
        }
        defaults.update(overrides)
        return weather_factor.Settings(**defaults)

    def test_fetch_today_rain_mm_reads_first_precipitation_value(self):
        settings = self._settings()
        payload = {"daily": {"precipitation_sum": [7.25]}}

        with patch.object(weather_factor, "urlopen", return_value=_FakeResponse(payload)) as mock_urlopen:
            rain_mm = weather_factor._fetch_today_rain_mm(settings)

        self.assertEqual(rain_mm, 7.25)
        request = mock_urlopen.call_args.args[0]
        self.assertIn("daily=precipitation_sum", request.full_url)
        self.assertEqual(mock_urlopen.call_args.kwargs["timeout"], settings.request_timeout_seconds)

    def test_fetch_today_rain_mm_clamps_negative_precipitation_to_zero(self):
        settings = self._settings()
        payload = {"daily": {"precipitation_sum": [-2.5]}}

        with patch.object(weather_factor, "urlopen", return_value=_FakeResponse(payload)):
            rain_mm = weather_factor._fetch_today_rain_mm(settings)

        self.assertEqual(rain_mm, 0.0)

    def test_fetch_today_rain_mm_raises_when_precipitation_missing(self):
        settings = self._settings()
        payload = {"daily": {"precipitation_sum": []}}

        with patch.object(weather_factor, "urlopen", return_value=_FakeResponse(payload)):
            with self.assertRaisesRegex(RuntimeError, "missing daily precipitation_sum"):
                weather_factor._fetch_today_rain_mm(settings)

    def test_fetch_today_rain_mm_wraps_network_errors(self):
        settings = self._settings()

        with patch.object(weather_factor, "urlopen", side_effect=URLError("temporary failure")):
            with self.assertRaisesRegex(RuntimeError, "Weather request failed"):
                weather_factor._fetch_today_rain_mm(settings)

    def test_compute_factor_value_scales_between_one_and_point_two(self):
        self.assertEqual(weather_factor._compute_factor_value(0.0, 20.0), 1.0)
        self.assertEqual(weather_factor._compute_factor_value(10.0, 20.0), 0.6)
        self.assertEqual(weather_factor._compute_factor_value(20.0, 20.0), 0.2)
        self.assertEqual(weather_factor._compute_factor_value(30.0, 20.0), 0.2)

    def test_compute_factor_value_returns_minimum_for_non_positive_scale(self):
        self.assertEqual(weather_factor._compute_factor_value(5.0, 0.0), 0.2)

    @unittest.skipUnless(
        os.getenv("RUN_ONLINE_TESTS") == "1",
        "Set RUN_ONLINE_TESTS=1 to run the live weather API integration test",
    )
    def test_fetch_today_rain_mm_live_api(self):
        settings = self._settings(
            latitude=float(os.getenv("ONLINE_TEST_LATITUDE", "52.52")),
            longitude=float(os.getenv("ONLINE_TEST_LONGITUDE", "13.405")),
            timezone=os.getenv("ONLINE_TEST_TIMEZONE", "auto"),
            request_timeout_seconds=int(os.getenv("ONLINE_TEST_TIMEOUT_SECONDS", "20")),
        )

        rain_mm = weather_factor._fetch_today_rain_mm(settings)
        print(f"Today's rain at {settings.latitude},{settings.longitude} is {rain_mm} mm")

        self.assertIsInstance(rain_mm, float)
        self.assertGreaterEqual(rain_mm, 0.0)
        self.assertLess(rain_mm, 500.0)


if __name__ == "__main__":
    unittest.main()