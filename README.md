# Torque Zone — Odoo 18 Community

Dockerized Odoo 18 with custom accounting addons, nginx, and GitHub Actions deploy.

## Secrets — never commit to this repo

| File / place | What goes there |
|--------------|-----------------|
| **`.env`** (local + server only) | `POSTGRES_PASSWORD`, `ODOO_ADMIN_PASSWORD` — already in `.gitignore` |
| **GitHub → Settings → Secrets → Actions** | `SSH_HOST`, `SSH_USER`, `SSH_PASSWORD` for auto-deploy |
| **This repository** | Code, `docker-compose.yml`, addons, nginx config — **no passwords** |

Copy `.env.example` to `.env` on the server and fill in values. The server keeps its own `/opt/torque-zone/.env`; deploy never overwrites it.

### GitHub Actions secrets (add in GitHub UI)

1. Open https://github.com/mohammed-f-zain/tourqe-zone/settings/secrets/actions
2. **New repository secret** for each:

| Name | Example value |
|------|----------------|
| `SSH_HOST` | `187.127.87.232` |
| `SSH_USER` | `root` |
| `SSH_PASSWORD` | your server SSH password |

Push to `main` runs `.github/workflows/deploy.yml` and syncs code to the server.

## Stack

- Odoo 18 Community (custom image with accounting Python deps)
- PostgreSQL 16
- Addons: `base_account_budget`, `base_accounting_kit`
- nginx + Let's Encrypt on the host

## DNS

| Type | Name | Value |
|------|------|--------|
| A | `@` | `187.127.87.232` |
| CNAME | `www` | `torque-zone.shop` |

If the site shows `DNS_PROBE_FINISHED_NXDOMAIN`, DNS is not visible on your network yet. Try:

- Flush DNS: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
- Use DNS `8.8.8.8` / `1.1.1.1` in macOS Network settings
- Test: `dig @8.8.8.8 torque-zone.shop A +short` → should print `187.127.87.232`

## Odoo (production)

- URL: https://torque-zone.shop/web/login
- Database: `torque_zone` (pre-created on server)
- Login/password: set on server — see `/opt/torque-zone/.env` and admin user on the instance

## Manual deploy

```bash
rsync -avz --exclude '.git' --exclude '.env' ./ root@YOUR_SERVER:/opt/torque-zone/
ssh root@YOUR_SERVER 'cd /opt/torque-zone && ./scripts/deploy.sh'
```

## Paths on server

- App: `/opt/torque-zone`
- Addons: `/opt/torque-zone/addons`
