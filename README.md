# Torque Zone — Odoo 18 + E-commerce Shop

Odoo 18 with accounting addons, COD e-commerce storefront, and GitHub Actions deploy.

## Local development

**Requires Docker Desktop** (start it first).

```bash
cp .env.example .env          # edit passwords if you like
./scripts/dev.sh              # starts Postgres + Odoo on http://localhost:8069
./scripts/init-local-db.sh    # first time only — creates DB + installs shop
```

| URL | Purpose |
|-----|---------|
| http://localhost:8069/web | Odoo backend (dashboard) |
| http://localhost:8069/shop | E-commerce storefront |

### After init

1. Open http://localhost:8069/web — set master password / admin if prompted  
2. **Inventory → Products** — create products, enable **Can be Sold** + **Show in Shop**  
3. **Sales → Orders** — website COD orders appear with delivery status  

## E-commerce (Torque Zone Shop)

- Products & categories from **Inventory** (`product.template`, `product.category`)
- **Cash on delivery** only — no online payment
- Checkout: name, phone, Jordan city, optional notes
- Orders flow into **Sales** with delivery statuses:
  - Pending → Confirmed → Preparing → Out for Delivery → Delivered (or Cancelled)

## Production server

- https://torque-zone.shop/web/login — backend  
- https://torque-zone.shop/shop — storefront (after installing `torque_zone_shop`)

## Secrets

Never commit `.env`. GitHub Actions secrets: `SSH_HOST`, `SSH_USER`, `SSH_PASSWORD`.

## Manual deploy

```bash
rsync -avz --exclude '.git' --exclude '.env' ./ root@YOUR_SERVER:/opt/torque-zone/
ssh root@YOUR_SERVER 'cd /opt/torque-zone && ./scripts/deploy.sh'
```
