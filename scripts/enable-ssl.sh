#!/usr/bin/env bash
# Run on the server as root to install or refresh Let's Encrypt (certbot).
set -euo pipefail

DOMAIN="torque-zone.shop"
EMAIL="${CERTBOT_EMAIL:-admin@${DOMAIN}}"

apt-get install -y certbot python3-certbot-nginx

certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" \
  --non-interactive --agree-tos --redirect -m "$EMAIL"

systemctl enable certbot.timer
systemctl start certbot.timer
nginx -t && systemctl reload nginx

certbot certificates
echo "HTTPS enabled: https://${DOMAIN}"
