#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/torque-zone}"
cd "$APP_DIR"

if [[ ! -f .env ]]; then
  echo "Missing .env in $APP_DIR — copy from .env.example and set secrets."
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

export POSTGRES_USER="${POSTGRES_USER:-odoo}"
export POSTGRES_DB="${POSTGRES_DB:-postgres}"

envsubst '${POSTGRES_USER} ${POSTGRES_PASSWORD} ${ODOO_ADMIN_PASSWORD}' \
  < config/odoo.conf.template > config/odoo.conf

docker compose pull db 2>/dev/null || true
docker compose build odoo
docker compose up -d --remove-orphans

echo "Deploy finished. Odoo: http://127.0.0.1:8069 (via nginx on public domain)"
