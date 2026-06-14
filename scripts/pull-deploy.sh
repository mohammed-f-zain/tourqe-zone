#!/usr/bin/env bash
# Run ON THE SERVER (cron every 2 min) to pull from GitHub and deploy.
# No inbound SSH from GitHub needed.
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/torque-zone}"
REPO_URL="${REPO_URL:-https://github.com/mohammed-f-zain/tourqe-zone.git}"
BRANCH="${BRANCH:-main}"
LOG="${APP_DIR}/logs/pull-deploy.log"

mkdir -p "$(dirname "$LOG")"
cd "$APP_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

if [[ ! -d .git ]]; then
  log "Initializing git repo..."
  git init -q
  git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
fi

git fetch origin "$BRANCH" -q
LOCAL="$(git rev-parse HEAD 2>/dev/null || echo none)"
REMOTE="$(git rev-parse "origin/${BRANCH}")"

if [[ "$LOCAL" == "$REMOTE" ]]; then
  exit 0
fi

log "New commit ${REMOTE:0:8} — deploying..."
git reset --hard "origin/${BRANCH}"
chmod +x scripts/deploy.sh scripts/pull-deploy.sh 2>/dev/null || true
./scripts/deploy.sh
log "Deploy complete."
