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

docker compose build odoo
docker compose stop odoo 2>/dev/null || true

# Wait for DB then upgrade custom shop module (picks up template/CSS changes)
ODOO_DB="${ODOO_DB:-torque_zone}"
echo "Upgrading torque_zone_shop on database ${ODOO_DB}..."
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d "${ODOO_DB}" \
  -u torque_zone_shop --load-language=ar_001 --stop-after-init
docker compose up -d --remove-orphans

echo "Waiting for Odoo to accept traffic..."
ready=0
for i in $(seq 1 40); do
  if curl -sf http://127.0.0.1:8069/web/health >/dev/null 2>&1; then
    ready=1
    echo "Odoo ready after ~${i} checks."
    break
  fi
  sleep 2
done
if [[ "$ready" -ne 1 ]]; then
  echo "WARNING: Odoo health check did not pass — site may show 502 briefly."
  docker logs torque_zone_odoo --tail 30 2>&1 || true
fi

if [[ -f nginx/torque-zone.shop.conf ]] && command -v nginx >/dev/null 2>&1; then
  echo "Updating nginx site config..."
  cp nginx/torque-zone.shop.conf /etc/nginx/sites-available/torque-zone.shop
  ln -sf /etc/nginx/sites-available/torque-zone.shop /etc/nginx/sites-enabled/torque-zone.shop
  if command -v certbot >/dev/null 2>&1 && [[ -d /etc/letsencrypt/live/torque-zone.shop ]]; then
    certbot --nginx -d torque-zone.shop -d www.torque-zone.shop \
      --non-interactive --agree-tos --redirect -m "admin@torque-zone.shop" 2>/dev/null || true
  fi
  nginx -t && systemctl reload nginx
fi

echo "Deploy finished. Site: https://torque-zone.shop"
