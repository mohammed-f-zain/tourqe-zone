#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit passwords if needed."
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

export POSTGRES_USER="${POSTGRES_USER:-odoo}"
export POSTGRES_DB="${POSTGRES_DB:-postgres}"

envsubst '${POSTGRES_USER} ${POSTGRES_PASSWORD} ${ODOO_ADMIN_PASSWORD}' \
  < config/odoo.local.conf.template > config/odoo.conf

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker Desktop, then run: ./scripts/dev.sh"
  exit 1
fi

docker compose -f docker-compose.local.yml build odoo
docker compose -f docker-compose.local.yml up -d --remove-orphans

echo ""
echo "Odoo local: http://localhost:8069"
echo "First run: create database, install Website + Inventory + Torque Zone Shop"
echo "Shop URL:   http://localhost:8069/shop"
