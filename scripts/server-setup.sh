#!/usr/bin/env bash
# One-time server bootstrap (run as root on Ubuntu 24.04)
set -euo pipefail

APP_DIR="/opt/torque-zone"
DOMAIN="torque-zone.shop"
EMAIL="${CERTBOT_EMAIL:-admin@${DOMAIN}}"

apt-get update
apt-get install -y nginx certbot python3-certbot-nginx gettext-base rsync git

mkdir -p /var/www/certbot
mkdir -p "$APP_DIR"

if [[ ! -f /etc/nginx/sites-available/torque-zone.shop ]]; then
  cp "$APP_DIR/nginx/torque-zone.shop.conf" /etc/nginx/sites-available/torque-zone.shop
  ln -sf /etc/nginx/sites-available/torque-zone.shop /etc/nginx/sites-enabled/torque-zone.shop
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl enable nginx
  systemctl reload nginx
fi

if [[ -f "$APP_DIR/scripts/deploy.sh" ]]; then
  chmod +x "$APP_DIR/scripts/deploy.sh"
  "$APP_DIR/scripts/deploy.sh"
fi

if host "$DOMAIN" >/dev/null 2>&1; then
  certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" \
    --non-interactive --agree-tos -m "$EMAIL" --redirect || true
  systemctl reload nginx
else
  echo "DNS for $DOMAIN not ready — skip certbot until A records point to this server."
fi

echo "Server setup complete."
