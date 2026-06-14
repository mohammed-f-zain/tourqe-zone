#!/usr/bin/env bash
# Deploy from your Mac when GitHub Actions cannot SSH to the server.
# Usage: SSH_PASSWORD='your-root-password' ./scripts/deploy-from-mac.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSH_HOST="${SSH_HOST:-187.127.87.232}"
SSH_USER="${SSH_USER:-root}"
SSH_OPTS=(-o StrictHostKeyChecking=no -o ConnectTimeout=30)

if [[ -z "${SSH_PASSWORD:-}" ]]; then
  echo "ERROR: Set SSH_PASSWORD with your server root password."
  echo ""
  echo "  SSH_PASSWORD='your-password' ./scripts/deploy-from-mac.sh"
  exit 1
fi

if ! command -v sshpass >/dev/null 2>&1; then
  echo "ERROR: sshpass not found. Install with: brew install sshpass"
  exit 1
fi

export SSHPASS="$SSH_PASSWORD"

echo "→ Syncing files to ${SSH_USER}@${SSH_HOST}..."
rsync -avz --delete \
  --exclude '.git' \
  --exclude '.env' \
  --exclude 'config/odoo.conf' \
  -e "sshpass -e ssh ${SSH_OPTS[*]}" \
  "${ROOT}/" "${SSH_USER}@${SSH_HOST}:/opt/torque-zone/"

echo "→ Running deploy on server..."
sshpass -e ssh "${SSH_OPTS[@]}" "${SSH_USER}@${SSH_HOST}" \
  "cd /opt/torque-zone && chmod +x scripts/deploy.sh scripts/pull-deploy.sh 2>/dev/null; ./scripts/deploy.sh"

echo "✓ Deploy finished — https://torque-zone.shop"
