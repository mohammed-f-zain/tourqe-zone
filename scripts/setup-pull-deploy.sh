#!/usr/bin/env bash
# One-time setup ON THE SERVER via SSH from your Mac:
#   SSH_PASSWORD='...' ./scripts/setup-pull-deploy.sh
set -euo pipefail

SSH_HOST="${SSH_HOST:-187.127.87.232}"
SSH_USER="${SSH_USER:-root}"

if [[ -z "${SSH_PASSWORD:-}" ]]; then
  echo "SSH_PASSWORD='your-password' ./scripts/setup-pull-deploy.sh"
  exit 1
fi

export SSHPASS="$SSH_PASSWORD"

echo "→ Installing pull-deploy cron on server..."
sshpass -e ssh -o StrictHostKeyChecking=no "${SSH_USER}@${SSH_HOST}" bash -s <<'REMOTE'
set -euo pipefail
APP_DIR="/opt/torque-zone"
mkdir -p "$APP_DIR/logs"
chmod +x "$APP_DIR/scripts/pull-deploy.sh" 2>/dev/null || true
CRON_LINE="*/2 * * * * ${APP_DIR}/scripts/pull-deploy.sh >> ${APP_DIR}/logs/pull-deploy.log 2>&1"
(crontab -l 2>/dev/null | grep -v pull-deploy.sh; echo "$CRON_LINE") | crontab -
echo "Cron installed — server will auto-deploy within 2 minutes of each git push."
REMOTE

echo "✓ Done. Future pushes deploy automatically without GitHub SSH."
