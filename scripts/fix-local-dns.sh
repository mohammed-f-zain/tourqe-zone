#!/usr/bin/env bash
# Run on your Mac when torque-zone.shop shows DNS_PROBE_FINISHED_NXDOMAIN
set -euo pipefail

IP="187.127.87.232"
DOMAIN="torque-zone.shop"

echo "=== Testing public DNS (Google) ==="
if dig "@8.8.8.8" "$DOMAIN" A +short | grep -q "$IP"; then
  echo "OK: Google DNS resolves $DOMAIN -> $IP"
else
  echo "WARN: Google DNS does not return $IP — fix records in Hostinger first."
fi

echo ""
echo "=== Testing your Mac resolver ==="
if dig "$DOMAIN" A +short | grep -q "$IP"; then
  echo "OK: Your Mac already resolves the domain."
  exit 0
fi

echo "Your Mac cannot resolve $DOMAIN (NXDOMAIN / empty)."
echo ""
echo "Option A — Flush DNS cache (needs password):"
echo "  sudo dscacheutil -flushcache"
echo "  sudo killall -HUP mDNSResponder"
echo ""
echo "Option B — Use Google DNS:"
echo "  System Settings → Network → Wi‑Fi → Details → DNS"
echo "  Add: 8.8.8.8 and 1.1.1.1"
echo ""
echo "Option C — Temporary hosts file (needs password):"
echo "  echo \"$IP $DOMAIN www.$DOMAIN\" | sudo tee -a /etc/hosts"
echo ""
echo "Option D — Open Odoo without DNS (works now):"
echo "  http://$IP/web/login"
