#!/usr/bin/env bash
# Fix torque-zone.shop on Mac when IP works but domain shows NXDOMAIN.
# Run: sudo bash scripts/fix-mac-dns.sh
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run with sudo:"
  echo "  sudo bash scripts/fix-mac-dns.sh"
  exit 1
fi

IP="187.127.87.232"
DOMAIN="torque-zone.shop"
REAL_USER="${SUDO_USER:-$USER}"

echo "=== 1) Set Google DNS on Wi-Fi ==="
networksetup -setdnsservers Wi-Fi 8.8.8.8 1.1.1.1

echo "=== 2) Flush DNS cache ==="
dscacheutil -flushcache
killall -HUP mDNSResponder 2>/dev/null || true

echo "=== 3) Add /etc/hosts entry ==="
MARKER="# torque-zone odoo"
if ! grep -q "$MARKER" /etc/hosts; then
  echo "$IP $DOMAIN www.$DOMAIN $MARKER" >> /etc/hosts
fi

echo "=== 4) Test (as $REAL_USER) ==="
sleep 2
su - "$REAL_USER" -c "dig $DOMAIN A +short" || true

echo ""
echo "Done. Open: https://$DOMAIN/web/login"
echo "(Spelling: torque-zone with Q — not tourqe-zone)"
