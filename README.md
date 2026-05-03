# Letrain Setup Guide (Fresh Raspberry Pi)

This guide walks you through a full Letrain installation on a clean Raspberry Pi OS system.
It also explains every environment variable used by Letrain scripts and services, with their runtime impact.

## What Letrain Installs

Running `./letrain-install.sh` sets up three systemd services:

- `letrain-tima.service`: runs the TiMa Docker stack (Mosquitto, backend, and optionally nginx)
- `letrain-consumer.service`: listens for execution events on MQTT and toggles GPIO relays
- `letrain-weather-factor.service`: fetches rain forecast from Open-Meteo and publishes a factor value via MQTT

## 1. Prepare a Fresh Raspberry Pi

1. Flash Raspberry Pi OS (Bookworm recommended; 64-bit preferred).
2. Boot the Pi, create your user, and connect to network.
3. Open a terminal on the Pi (or SSH in).
4. Update the base OS:

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

## 2. Install Prerequisites

Letrain installer requires at least `git` and `docker` to be available.

1. Install required packages:

```bash
sudo apt-get install -y git ca-certificates curl docker.io docker-compose-plugin
```

2. Enable Docker:

```bash
sudo systemctl enable --now docker
```

3. Optional but recommended: allow your user to run Docker without `sudo`:

```bash
sudo usermod -aG docker "$USER"
```

4. Log out and back in once (or reboot) so group changes apply.

## 3. Clone Letrain

Choose a working directory and clone:

```bash
cd "$HOME"
git clone https://github.com/nielssiebert/letrain.git
cd letrain
chmod +x letrain-install.sh
```

## 4. Run the Installer

Start installation:

```bash
./letrain-install.sh
```

The script clones TiMa (if needed), runs TiMa's installer, writes Letrain env files, creates systemd units, and starts services.

### Installer Prompts and Recommended Answers

1. `Letrain install root directory` (default: `~/letrain-deploy`)
- Where deployment artifacts and env files are stored.
- Keep default unless you need another disk/path.

2. `Docker stack name` (default: `letrain`)
- Docker compose project name.
- Change if multiple stacks run on the same host.

3. `Domain (or localhost)` (default: `localhost`)
- Hostname used by TiMa/nginx routing.
- Use `localhost` for local-only access.

4. `App path prefix` (default: `/letrain`)
- URL path prefix where UI is served.
- Example: `/letrain` means UI at `http://host/letrain/`.

5. `Browser tab title` (default: `Letrain`)
- UI title branding.

6. `Translation replacement JSON file` (default: `translation-replacements.letrain.json`)
- Replacement map used while integrating Letrain branding text.

7. `Custom icon file` (default: `Letrain.png`)
- UI icon/branding asset.

8. `Use your own nginx instance` (`yes`/`no`, default: `no`)
- `no`: stack includes nginx service.
- `yes`: stack excludes nginx; you must reverse-proxy yourself.

9. `Enable Let's Encrypt + certbot` (shown only if domain is not `localhost` and own nginx is `no`)
- Enables certbot-based TLS provisioning.

10. `Let's Encrypt email` (shown only when LE is enabled)
- Contact email for certificate management.

## 5. Verify Services

Check all services are active:

```bash
sudo systemctl is-active letrain-tima.service letrain-consumer.service letrain-weather-factor.service
```

Inspect details:

```bash
sudo systemctl --no-pager --full status letrain-tima letrain-consumer letrain-weather-factor
```

View recent logs:

```bash
sudo journalctl -u letrain-tima -u letrain-consumer -u letrain-weather-factor -n 100 --no-pager
```

## 6. Edit Runtime Environment Variables

After install, Letrain writes two runtime env files:

- `~/letrain-deploy/deploy/letrain-consumer.env`
- `~/letrain-deploy/deploy/letrain-weather-factor.env`

If you changed install root, replace `~/letrain-deploy` with your chosen path.

After edits, restart services:

```bash
sudo systemctl restart letrain-consumer letrain-weather-factor
```

## 7. Full Environment Variable Reference

This section covers all env vars consumed directly by Letrain code or Letrain installer.

## 7.1 Installer-Level Variable

### `TIMA_REPO_URL`
- Default: `git@github.com:nielssiebert/TiMa.git`
- Used by: `letrain-install.sh`
- Impact:
  - Controls where TiMa is cloned from.
  - Useful for forks, local mirrors, or HTTPS-only environments.
  - If SSH clone fails, installer retries with HTTPS conversion automatically.

Example:

```bash
TIMA_REPO_URL=https://github.com/nielssiebert/TiMa.git ./letrain-install.sh
```

## 7.2 Shared MQTT Variables (Used by Consumer and Weather Service)

### `MQTT_HOST`
- Default: `127.0.0.1`
- Used by: both Python services
- Impact:
  - MQTT broker hostname/IP.
  - Wrong value prevents message publish/subscribe.

### `MQTT_PORT`
- Default: `1883`
- Used by: both Python services
- Impact:
  - Broker TCP port.
  - Invalid integer falls back to default and logs warning.

### `MQTT_TOPIC`
- Consumer default file value: `tima/execution-events`
- Weather default file value: `tima/factors/values`
- Used by: both Python services
- Impact:
  - Consumer subscribes to this topic.
  - Weather service publishes factor payloads to this topic.
  - Topic mismatch is a common reason for "nothing happens" symptoms.

### `MQTT_QOS`
- Default: `1`
- Used by: both Python services
- Impact:
  - MQTT Quality of Service for subscribe/publish.
  - `1` (at least once) is resilient but can duplicate messages in failure scenarios.

### `LETRAIN_LOG_LEVEL`
- Default: `INFO`
- Used by: both Python services
- Impact:
  - Controls Python logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, ...).
  - Useful for troubleshooting MQTT, payload parsing, and API issues.

## 7.3 Consumer-Specific Variables (`letrain-consumer.env`)

### `RELAY_ACTIVE_LOW`
- Default: `false`
- Used by: relay output logic
- Impact:
  - `false`: relay ON => GPIO HIGH, OFF => GPIO LOW.
  - `true`: logic is inverted (active-low relay boards).
  - Important for avoiding inverted relay behavior.

Accepted true values: `1`, `true`, `yes`, `on` (case-insensitive).
Any other value becomes false.

### `LETRAIN_DEFAULT_PIN`
- Default: unset
- Used by: message pin fallback
- Impact:
  - If incoming MQTT payload has no `pin`, this fallback is used.
  - If unset and payload has no pin, consumer ignores message with warning.
  - Helpful when controlling a single fixed relay channel.

Payload behavior summary:

- Expected action values: `START` or `STOP`.
- If action is missing/other value: message ignored.
- Pin source: payload `pin` first, then `LETRAIN_DEFAULT_PIN`.

## 7.4 Weather-Service Variables (`letrain-weather-factor.env`)

### `MQTT_OPERATION_TIMEOUT_SECONDS`
- Default: `15`
- Used by: publish ACK wait loop
- Impact:
  - Max wait for MQTT PUBACK (for QoS > 0).
  - Too low can create false timeout errors on slow networks.
  - Too high delays failure detection.

### `FACTOR_ID`
- Default: `weather_forecast`
- Used by: published payload (`factor_id` and `id`)
- Impact:
  - Identity key of the weather factor in downstream systems.
  - Must match expected factor identifier in TiMa/backend logic.

### `WEATHER_LATITUDE`
- Default: `52.52`
- Used by: Open-Meteo query
- Impact:
  - Changes forecast location.

### `WEATHER_LONGITUDE`
- Default: `13.405`
- Used by: Open-Meteo query
- Impact:
  - Changes forecast location.

### `WEATHER_TIMEZONE`
- Default: `auto`
- Used by: Open-Meteo query parameter
- Impact:
  - Affects day boundary and interpretation of daily forecast.
  - `auto` is usually safe; explicit timezone can improve predictability.

### `WEATHER_API_BASE_URL`
- Default: `https://api.open-meteo.com/v1/forecast`
- Used by: HTTP request URL generation
- Impact:
  - Allows custom endpoint/proxy/testing backend.
  - Wrong URL causes repeated fetch failures and error logs.

### `WEATHER_REQUEST_TIMEOUT_SECONDS`
- Default: `20`
- Used by: HTTP client timeout
- Impact:
  - Network timeout for weather API call.
  - Too low can fail under temporary network latency.

### `WEATHER_PUBLISH_INTERVAL_SECONDS`
- Installer default written to env file: `43200` (12h)
- Internal fallback in code if missing/invalid: `21600` (6h)
- Used by: main publish loop delay
- Impact:
  - Controls how often factor is refreshed and republished.
  - Lower values increase API calls and MQTT traffic.

### `WEATHER_RAIN_FULL_SCALE_MM`
- Default: `20.0`
- Used by: normalization formula
- Impact:
  - Formula: `factor = 1 - clamp(rain_mm, 0, full_scale) / full_scale`
  - Rain at or above full scale gives factor `0.0`.
  - No rain gives factor `1.0`.
  - Lowering this value makes the factor drop faster for the same rain amount.

## 7.5 Parsing and Fallback Rules (Important in Production)

- Integer vars: invalid values are ignored and replaced by built-in defaults (warning logged).
- Float vars: invalid values are ignored and replaced by built-in defaults (warning logged).
- Bool var (`RELAY_ACTIVE_LOW`): only explicit truthy values become true.
- Missing critical values do not crash startup in most cases because defaults are used.
  - This improves resilience but can hide misconfiguration if logs are not monitored.

## 7.6 Test-Only Variables (Not Used by Services)

These variables are only used by `test_letrain_weather_factor.py` when running optional live API tests.

### `RUN_ONLINE_TESTS`
- Default behavior: online test is skipped unless this is set to `1`.
- Impact:
  - Prevents CI/local test runs from depending on internet access by default.

### `ONLINE_TEST_LATITUDE`
- Default: `52.52`
- Impact:
  - Overrides test location for the live API test.

### `ONLINE_TEST_LONGITUDE`
- Default: `13.405`
- Impact:
  - Overrides test location for the live API test.

### `ONLINE_TEST_TIMEZONE`
- Default: `auto`
- Impact:
  - Controls timezone used in the live API test request.

### `ONLINE_TEST_TIMEOUT_SECONDS`
- Default: `20`
- Impact:
  - HTTP timeout used by the live API test.

## 8. Common Post-Install Tweaks

1. Change MQTT broker host:
- Edit both env files and set `MQTT_HOST=<broker-ip-or-hostname>`.

2. Use one fixed relay GPIO pin:
- Add `LETRAIN_DEFAULT_PIN=17` to `letrain-consumer.env`.

3. Tune weather aggressiveness:
- Reduce `WEATHER_RAIN_FULL_SCALE_MM` to make factor react more strongly to small rain forecasts.

4. Increase debug logging temporarily:
- Set `LETRAIN_LOG_LEVEL=DEBUG` and restart services.

## 9. Service Management Cheat Sheet

```bash
# Restart all Letrain services
sudo systemctl restart letrain-tima letrain-consumer letrain-weather-factor

# Tail consumer logs
sudo journalctl -u letrain-consumer -f

# Tail weather logs
sudo journalctl -u letrain-weather-factor -f

# Show failed units
sudo systemctl --failed --no-legend
```

## Notes About TiMa `.env`

Letrain also relies on TiMa-generated deployment variables in `~/letrain-deploy/deploy/.env`.
Those variables are owned by the TiMa project and can vary by TiMa version.

For Letrain operation, the variables documented above are the complete set directly consumed by Letrain installer and Letrain Python services.