#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() {
  printf '[letrain-install] %s\n' "$1"
}

die() {
  printf '[letrain-install][error] %s\n' "$1" >&2
  exit 1
}

run_root() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
    return
  fi
  if command -v sudo >/dev/null 2>&1; then
    sudo "$@"
    return
  fi
  die "This step requires root privileges and sudo is not installed."
}

prompt_default() {
  local key="$1"
  local default_value="$2"
  local input
  read -r -p "$key [$default_value]: " input
  if [[ -z "$input" ]]; then
    printf '%s\n' "$default_value"
    return
  fi
  printf '%s\n' "$input"
}

prompt_yes_no() {
  local key="$1"
  local default_value="$2"
  local input
  local normalized
  read -r -p "$key [$default_value]: " input
  input="${input:-$default_value}"
  normalized="$(printf '%s' "$input" | tr '[:upper:]' '[:lower:]')"
  case "$normalized" in
    y|yes) printf 'yes\n' ;;
    n|no) printf 'no\n' ;;
    *) die "Invalid answer for '$key'. Use yes or no." ;;
  esac
}

normalize_path_prefix() {
  local raw="$1"
  if [[ -z "$raw" || "$raw" == "/" ]]; then
    printf '/\n'
    return
  fi
  local prefixed="$raw"
  if [[ "${prefixed:0:1}" != "/" ]]; then
    prefixed="/$prefixed"
  fi
  prefixed="${prefixed%/}"
  printf '%s\n' "$prefixed"
}

resolve_path() {
  local raw="$1"
  if [[ "$raw" == ~/* ]]; then
    printf '%s/%s\n' "$HOME" "${raw#~/}"
    return
  fi
  printf '%s\n' "$raw"
}

ensure_command() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || die "Missing required command: $cmd"
}

git_repo_url_to_https() {
  local repo_url="$1"
  if [[ "$repo_url" =~ ^git@([^:]+):(.+)$ ]]; then
    printf 'https://%s/%s\n' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    return
  fi
  if [[ "$repo_url" =~ ^ssh://git@([^/]+)/(.+)$ ]]; then
    printf 'https://%s/%s\n' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    return
  fi
  printf '%s\n' "$repo_url"
}

ensure_tima_repository() {
  local repo_url="$1"
  local repo_path="$2"

  if [[ -d "$repo_path/.git" ]]; then
    log "TiMa repository already exists at $repo_path"
    return
  fi

  if [[ -e "$repo_path" ]]; then
    die "Path exists but is not a git repository: $repo_path"
  fi

  log "Cloning TiMa repository from $repo_url to $repo_path"
  if git clone "$repo_url" "$repo_path"; then
    return
  fi

  local https_url
  https_url="$(git_repo_url_to_https "$repo_url")"
  if [[ "$https_url" == "$repo_url" ]]; then
    die "Unable to clone TiMa repository from: $repo_url"
  fi

  log "SSH clone failed; retrying TiMa clone via HTTPS: $https_url"
  rm -rf "$repo_path"
  git clone "$https_url" "$repo_path" || die "Unable to clone TiMa repository from either SSH or HTTPS."
}

install_consumer_packages() {
  if ! command -v apt-get >/dev/null 2>&1; then
    log "apt-get not available; skipping package installation."
    return
  fi
  log "Installing MQTT/GPIO dependencies for letrain-consumer.py"
  run_root apt-get update -y
  run_root apt-get install -y python3 python3-paho-mqtt python3-rpi.gpio
}

run_tima_installer() {
  local tima_install_script="$1"
  local tima_repo_input="$2"
  local install_root="$3"
  local stack_name="$4"
  local domain="$5"
  local app_prefix="$6"
  local app_title="$7"
  local translation_file="$8"
  local icon_file="$9"
  local use_own_nginx="${10}"
  local enable_letsencrypt="${11}"
  local letsencrypt_email="${12}"

  local responses=(
    "$tima_repo_input"
    "$install_root"
    "$stack_name"
    "$domain"
    "$app_prefix"
    "$app_title"
    "$translation_file"
    "$icon_file"
    "$use_own_nginx"
  )

  if [[ "$use_own_nginx" == "no" && "$domain" != "localhost" ]]; then
    responses+=("$enable_letsencrypt")
    if [[ "$enable_letsencrypt" == "yes" ]]; then
      responses+=("$letsencrypt_email")
    fi
  fi

  responses+=("no")

  log "Running TiMa install.sh with predefined LeTrain settings"
  printf '%s\n' "${responses[@]}" | bash "$tima_install_script"
}

run_tima_installer_with_fallback() {
  local tima_install_script="$1"
  local tima_repo_input="$2"
  local install_root="$3"
  local stack_name="$4"
  local domain="$5"
  local app_prefix="$6"
  local app_title="$7"
  local translation_file="$8"
  local icon_file="$9"
  local use_own_nginx="${10}"
  local enable_letsencrypt="${11}"
  local letsencrypt_email="${12}"

  if run_tima_installer \
    "$tima_install_script" \
    "$tima_repo_input" \
    "$install_root" \
    "$stack_name" \
    "$domain" \
    "$app_prefix" \
    "$app_title" \
    "$translation_file" \
    "$icon_file" \
    "$use_own_nginx" \
    "$enable_letsencrypt" \
    "$letsencrypt_email"; then
    return
  fi

  if [[ -n "$translation_file" ]]; then
    log "TiMa installer failed; retrying once with translation replacements disabled."
    if run_tima_installer \
      "$tima_install_script" \
      "$tima_repo_input" \
      "$install_root" \
      "$stack_name" \
      "$domain" \
      "$app_prefix" \
      "$app_title" \
      "" \
      "$icon_file" \
      "$use_own_nginx" \
      "$enable_letsencrypt" \
      "$letsencrypt_email"; then
      return
    fi
  fi

  if [[ "$use_own_nginx" == "no" ]]; then
    log "TiMa installer still failing; retrying once with external nginx mode enabled."
    run_tima_installer \
      "$tima_install_script" \
      "$tima_repo_input" \
      "$install_root" \
      "$stack_name" \
      "$domain" \
      "$app_prefix" \
      "$app_title" \
      "" \
      "$icon_file" \
      "yes" \
      "no" \
      ""
    return
  fi

  return 1
}

write_compose_launcher() {
  local launcher_path="$1"
  local stack_name="$2"
  local env_file="$3"
  local compose_file="$4"
  local services_csv="$5"

  cat > "$launcher_path" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail

ACTION="\${1:-up}"
if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  echo "docker compose command not found" >&2
  exit 1
fi

COMMON_ARGS=(-p "$stack_name" --env-file "$env_file" -f "$compose_file")
SERVICES=($services_csv)

case "\$ACTION" in
  up)
    "\${COMPOSE[@]}" "\${COMMON_ARGS[@]}" up -d "\${SERVICES[@]}"
    ;;
  down)
    "\${COMPOSE[@]}" "\${COMMON_ARGS[@]}" down
    ;;
  restart)
    "\${COMPOSE[@]}" "\${COMMON_ARGS[@]}" down
    "\${COMPOSE[@]}" "\${COMMON_ARGS[@]}" up -d "\${SERVICES[@]}"
    ;;
  *)
    echo "Usage: \$0 {up|down|restart}" >&2
    exit 2
    ;;
esac
EOF
  chmod +x "$launcher_path"
}

create_systemd_services() {
  local compose_launcher="$1"
  local consumer_script="$2"
  local consumer_env_file="$3"
  local weather_script="$4"
  local weather_env_file="$5"

  cat <<EOF | run_root tee /etc/systemd/system/letrain-tima.service >/dev/null
[Unit]
Description=LeTrain TiMa Docker stack
After=network-online.target docker.service
Wants=network-online.target docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=$compose_launcher up
ExecStop=$compose_launcher down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

  cat <<EOF | run_root tee /etc/systemd/system/letrain-consumer.service >/dev/null
[Unit]
Description=LeTrain MQTT relay consumer
After=network-online.target letrain-tima.service
Wants=network-online.target letrain-tima.service
Requires=letrain-tima.service

[Service]
Type=simple
EnvironmentFile=$consumer_env_file
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $consumer_script
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

  cat <<EOF | run_root tee /etc/systemd/system/letrain-weather-factor.service >/dev/null
[Unit]
Description=LeTrain weather factor publisher
After=network-online.target letrain-tima.service
Wants=network-online.target letrain-tima.service
Requires=letrain-tima.service

[Service]
Type=simple
EnvironmentFile=$weather_env_file
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $weather_script
Restart=always
RestartSec=10
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
EOF

  run_root systemctl daemon-reload
  run_root systemctl enable --now letrain-tima.service
  run_root systemctl enable --now letrain-consumer.service
  run_root systemctl enable --now letrain-weather-factor.service
}

main() {
  ensure_command git
  ensure_command docker

  local tima_repo_url="${TIMA_REPO_URL:-git@github.com:nielssiebert/TiMa.git}"
  local tima_repo_input
  tima_repo_input="$(git_repo_url_to_https "$tima_repo_url")"
  local tima_repo_path
  tima_repo_path="$(resolve_path "$SCRIPT_DIR/../TiMa")"
  ensure_tima_repository "$tima_repo_url" "$tima_repo_path"

  local tima_install_script="$tima_repo_path/install.sh"
  [[ -f "$tima_install_script" ]] || die "TiMa install.sh not found at: $tima_install_script"

  local install_root
  install_root="$(resolve_path "$(prompt_default "LeTrain install root directory" "$HOME/letrain-deploy")")"
  local stack_name
  stack_name="$(prompt_default "Docker stack name" "letrain")"
  local domain
  domain="$(prompt_default "Domain (or localhost)" "localhost")"
  local app_prefix
  app_prefix="$(normalize_path_prefix "$(prompt_default "App path prefix" "/letrain")")"
  local app_title
  app_title="$(prompt_default "Browser tab title" "Letrain")"

  local default_translation="$SCRIPT_DIR/translation-replacements.letrain.json"
  local translation_file
  translation_file="$(resolve_path "$(prompt_default "Translation replacement JSON file" "$default_translation")")"
  [[ -f "$translation_file" ]] || die "Translation file not found: $translation_file"

  local default_icon="$SCRIPT_DIR/Letrain.png"
  local icon_file
  icon_file="$(resolve_path "$(prompt_default "Custom icon file" "$default_icon")")"
  [[ -f "$icon_file" ]] || die "Icon file not found: $icon_file"

  local use_own_nginx
  use_own_nginx="$(prompt_yes_no "Use your own nginx instance" "no")"

  local enable_letsencrypt="no"
  local letsencrypt_email=""
  if [[ "$use_own_nginx" == "no" && "$domain" != "localhost" ]]; then
    enable_letsencrypt="$(prompt_yes_no "Enable Let's Encrypt + certbot" "no")"
    if [[ "$enable_letsencrypt" == "yes" ]]; then
      letsencrypt_email="$(prompt_default "Let's Encrypt email" "admin@$domain")"
    fi
  fi

  install_consumer_packages

  run_tima_installer_with_fallback \
    "$tima_install_script" \
    "$tima_repo_input" \
    "$install_root" \
    "$stack_name" \
    "$domain" \
    "$app_prefix" \
    "$app_title" \
    "$translation_file" \
    "$icon_file" \
    "$use_own_nginx" \
    "$enable_letsencrypt" \
    "$letsencrypt_email"

  local deploy_env="$install_root/deploy/.env"
  local compose_file="$install_root/repository/deploy/docker-compose.rpi.yml"
  [[ -f "$deploy_env" ]] || die "Expected deploy env file not found: $deploy_env"
  [[ -f "$compose_file" ]] || die "Expected compose file not found: $compose_file"

  local compose_launcher="$install_root/deploy/letrain-compose.sh"
  local services_csv="mosquitto backend"
  if [[ "$use_own_nginx" == "no" ]]; then
    services_csv="mosquitto backend nginx"
  fi
  write_compose_launcher "$compose_launcher" "$stack_name" "$deploy_env" "$compose_file" "$services_csv"

  local consumer_env="$install_root/deploy/letrain-consumer.env"
  cat > "$consumer_env" <<EOF
MQTT_HOST=127.0.0.1
MQTT_PORT=1883
MQTT_TOPIC=tima/execution-events
MQTT_QOS=1
RELAY_ACTIVE_LOW=false
LETRAIN_LOG_LEVEL=INFO
EOF

  local consumer_script="$SCRIPT_DIR/letrain-consumer.py"
  [[ -f "$consumer_script" ]] || die "Missing consumer script at: $consumer_script"

  local weather_env="$install_root/deploy/letrain-weather-factor.env"
  cat > "$weather_env" <<EOF
MQTT_HOST=127.0.0.1
MQTT_PORT=1883
MQTT_TOPIC=tima/factors/values
MQTT_QOS=1
MQTT_OPERATION_TIMEOUT_SECONDS=15
FACTOR_ID=weather_forecast
WEATHER_LATITUDE=52.52
WEATHER_LONGITUDE=13.405
WEATHER_TIMEZONE=auto
WEATHER_API_BASE_URL=https://api.open-meteo.com/v1/forecast
WEATHER_REQUEST_TIMEOUT_SECONDS=20
WEATHER_PUBLISH_INTERVAL_SECONDS=43200
WEATHER_RAIN_FULL_SCALE_MM=20.0
LETRAIN_LOG_LEVEL=INFO
EOF

  local weather_script="$SCRIPT_DIR/letrain-weather-factor.py"
  [[ -f "$weather_script" ]] || die "Missing weather publisher script at: $weather_script"

  create_systemd_services "$compose_launcher" "$consumer_script" "$consumer_env" "$weather_script" "$weather_env"

  log "LeTrain installation complete."
  log "You can edit $consumer_env to tune MQTT topic and relay behavior."
  log "You can edit $weather_env to tune weather location and publish cadence."
  log "Check status with: sudo systemctl status letrain-tima letrain-consumer letrain-weather-factor"
}

main "$@"
