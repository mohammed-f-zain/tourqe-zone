#!/usr/bin/env bash
# Initialize local Odoo database with shop modules (run after ./scripts/dev.sh)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DB_NAME="${1:-torque_zone_local}"

docker compose -f docker-compose.local.yml run --rm odoo odoo \
  -c /etc/odoo/odoo.conf \
  -d "$DB_NAME" \
  -i base,website,sale,sale_stock,stock,product,torque_zone_shop \
  --without-demo=all \
  --stop-after-init

echo ""
echo "Database '$DB_NAME' ready."
echo "Odoo:     http://localhost:8069"
echo "Shop:     http://localhost:8069/shop"
echo "Backend:  http://localhost:8069/web — create admin on first login if new DB"
