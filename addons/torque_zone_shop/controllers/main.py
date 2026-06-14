# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request

from odoo.addons.torque_zone_shop.const import JORDAN_CITIES, JORDAN_CITIES_AR


class TorqueZoneShop(http.Controller):

    # ── Session / cart helpers ──────────────────────────────────────────

    def _get_cart(self):
        return request.session.get('torque_cart', {'lines': []})

    def _save_cart(self, cart):
        request.session['torque_cart'] = cart

    def _cart_count(self):
        cart = self._get_cart()
        return sum(line.get('qty', 0) for line in cart.get('lines', []))

    def _is_rtl(self):
        return request.env.lang.startswith('ar')

    def _get_jordan_cities(self):
        if self._is_rtl():
            return JORDAN_CITIES_AR
        return JORDAN_CITIES

    def _city_labels(self):
        return dict(self._get_jordan_cities())

    def _page_ctx(self, active_page, **extra):
        return {
            'cart_count': self._cart_count(),
            'active_page': active_page,
            'is_rtl': self._is_rtl(),
            'jordan_cities': self._get_jordan_cities(),
            **extra,
        }

    def _get_products_domain(self, category_id=None):
        domain = [
            ('sale_ok', '=', True),
            ('torque_shop_published', '=', True),
            ('active', '=', True),
        ]
        if category_id:
            domain.append(('categ_id', 'child_of', int(category_id)))
        return domain

    def _product_image_url(self, product):
        if product.image_512:
            return f'/web/image/product.template/{product.id}/image_512'
        return '/torque_zone_shop/static/src/img/placeholder.svg'

    def _enrich_cart_lines(self, cart):
        Product = request.env['product.template'].sudo()
        lines = []
        for item in cart.get('lines', []):
            product = Product.browse(item['product_id']).exists()
            if not product or not product.torque_shop_published:
                continue
            qty = max(1, int(item.get('qty', 1)))
            lines.append({
                'product': product,
                'product_id': product.id,
                'name': product.name,
                'qty': qty,
                'price': product.list_price,
                'subtotal': product.list_price * qty,
                'image_url': self._product_image_url(product),
            })
        return lines

    def _get_categories(self):
        return request.env['product.category'].sudo().search([
            ('parent_id', '=', False),
            ('product_count', '>', 0),
        ], order='name')

    # ── Website pages ───────────────────────────────────────────────────

    @http.route(['/', '/home'], type='http', auth='public', website=True, sitemap=True)
    def page_home(self, **kw):
        Product = request.env['product.template'].sudo()
        domain = self._get_products_domain()
        featured = Product.search(domain, order='write_date desc', limit=8)
        categories = self._get_categories()
        return request.render('torque_zone_shop.page_home', self._page_ctx(
            'home', featured_products=featured, categories=categories,
        ))

    @http.route('/about', type='http', auth='public', website=True, sitemap=True)
    def page_about(self, **kw):
        return request.render('torque_zone_shop.page_about', self._page_ctx('about'))

    @http.route('/contact', type='http', auth='public', website=True, sitemap=True)
    def page_contact(self, **kw):
        return request.render('torque_zone_shop.page_contact', self._page_ctx('contact'))

    # ── Shop ────────────────────────────────────────────────────────────

    @http.route(['/shop', '/shop/page/<int:page>'], type='http', auth='public', website=True)
    def shop_catalog(self, page=1, search='', category_id=None, **kw):
        Product = request.env['product.template'].sudo()
        domain = self._get_products_domain(category_id)
        if search:
            domain.append(('name', 'ilike', search))

        products = Product.search(domain, order='name', limit=24, offset=(page - 1) * 24)
        total = Product.search_count(domain)

        return request.render('torque_zone_shop.shop_catalog', self._page_ctx(
            'shop',
            products=products,
            categories=self._get_categories(),
            search=search,
            category_id=int(category_id) if category_id else None,
            page=page,
            total_pages=max(1, (total + 23) // 24),
        ))

    @http.route('/shop/category/<int:category_id>', type='http', auth='public', website=True)
    def shop_category(self, category_id, page=1, search='', **kw):
        category = request.env['product.category'].sudo().browse(category_id)
        if not category.exists():
            return request.redirect('/shop')

        Product = request.env['product.template'].sudo()
        domain = self._get_products_domain(category_id)
        if search:
            domain.append(('name', 'ilike', search))

        products = Product.search(domain, order='name', limit=24, offset=(page - 1) * 24)
        total = Product.search_count(domain)

        return request.render('torque_zone_shop.shop_catalog', self._page_ctx(
            'shop',
            products=products,
            categories=self._get_categories(),
            category=category,
            search=search,
            category_id=category_id,
            page=page,
            total_pages=max(1, (total + 23) // 24),
        ))

    @http.route('/shop/product/<int:product_id>', type='http', auth='public', website=True)
    def shop_product(self, product_id, **kw):
        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists() or not product.torque_shop_published or not product.sale_ok:
            return request.redirect('/shop')

        related = request.env['product.template'].sudo().search([
            ('categ_id', '=', product.categ_id.id),
            ('id', '!=', product.id),
            ('torque_shop_published', '=', True),
            ('sale_ok', '=', True),
        ], limit=4)

        return request.render('torque_zone_shop.shop_product', self._page_ctx(
            'shop',
            product=product,
            related_products=related,
            image_url=self._product_image_url(product),
        ))

    @http.route('/shop/cart', type='http', auth='public', website=True)
    def shop_cart(self, **kw):
        cart = self._get_cart()
        lines = self._enrich_cart_lines(cart)
        total = sum(line['subtotal'] for line in lines)
        return request.render('torque_zone_shop.shop_cart', self._page_ctx(
            'cart', lines=lines, total=total, journey_step='cart',
        ))

    @http.route('/shop/cart/add', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def shop_cart_add(self, product_id, qty=1, **kw):
        product = request.env['product.template'].sudo().browse(int(product_id))
        if not product.exists() or not product.torque_shop_published:
            return request.redirect('/shop')

        cart = self._get_cart()
        qty = max(1, int(qty))
        for line in cart['lines']:
            if line['product_id'] == product.id:
                line['qty'] += qty
                break
        else:
            cart['lines'].append({'product_id': product.id, 'qty': qty})
        self._save_cart(cart)
        return request.redirect(kw.get('redirect', '/shop/cart'))

    @http.route('/shop/cart/update', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def shop_cart_update(self, **post):
        cart = self._get_cart()
        new_lines = []
        for line in cart.get('lines', []):
            key = f"qty_{line['product_id']}"
            if key in post and int(post.get(key, 0)) > 0:
                line['qty'] = int(post[key])
                new_lines.append(line)
        cart['lines'] = new_lines
        self._save_cart(cart)
        return request.redirect('/shop/cart')

    @http.route('/shop/cart/inc/<int:product_id>', type='http', auth='public', website=True)
    def shop_cart_inc(self, product_id, **kw):
        cart = self._get_cart()
        for line in cart.get('lines', []):
            if line['product_id'] == product_id:
                line['qty'] = line.get('qty', 1) + 1
                break
        self._save_cart(cart)
        return request.redirect(kw.get('redirect', '/shop/cart'))

    @http.route('/shop/cart/dec/<int:product_id>', type='http', auth='public', website=True)
    def shop_cart_dec(self, product_id, **kw):
        cart = self._get_cart()
        new_lines = []
        for line in cart.get('lines', []):
            if line['product_id'] == product_id:
                if line.get('qty', 1) <= 1:
                    continue
                line['qty'] -= 1
            new_lines.append(line)
        cart['lines'] = new_lines
        self._save_cart(cart)
        return request.redirect(kw.get('redirect', '/shop/cart'))

    @http.route('/shop/cart/remove/<int:product_id>', type='http', auth='public', website=True)
    def shop_cart_remove(self, product_id, **kw):
        cart = self._get_cart()
        cart['lines'] = [l for l in cart.get('lines', []) if l['product_id'] != product_id]
        self._save_cart(cart)
        return request.redirect('/shop/cart')

    @http.route('/shop/checkout', type='http', auth='public', website=True)
    def shop_checkout(self, **kw):
        lines = self._enrich_cart_lines(self._get_cart())
        if not lines:
            return request.redirect('/shop/cart')
        return request.render('torque_zone_shop.shop_checkout', self._page_ctx(
            'cart',
            lines=lines,
            total=sum(l['subtotal'] for l in lines),
            journey_step='checkout',
        ))

    @http.route('/shop/order/confirm', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def shop_order_confirm(self, **post):
        cart = self._get_cart()
        lines = self._enrich_cart_lines(cart)
        if not lines:
            return request.redirect('/shop/cart')

        name = (post.get('customer_name') or '').strip()
        phone = (post.get('phone_number') or '').strip()
        address = (post.get('address') or '').strip()
        city = (post.get('city') or '').strip()
        city_labels = dict(JORDAN_CITIES)

        errors = []
        if not name:
            errors.append(_('Please enter your name.'))
        if not phone:
            errors.append(_('Please enter your phone number.'))
        if not address:
            errors.append(_('Please enter your delivery address.'))
        if not city or city not in city_labels:
            errors.append(_('Please select your city.'))

        if errors:
            return request.render('torque_zone_shop.shop_checkout', self._page_ctx(
                'cart',
                lines=lines,
                total=sum(l['subtotal'] for l in lines),
                journey_step='checkout',
                errors=errors,
                form=post,
            ))

        env = request.env
        Partner = env['res.partner'].sudo()
        SaleOrder = env['sale.order'].sudo()
        jordan = env.ref('base.jo', raise_if_not_found=False)

        partner = Partner.search([('phone', '=', phone), ('name', '=', name)], limit=1)
        vals = {
            'name': name,
            'phone': phone,
            'street': address,
            'city': city_labels.get(city, city),
            'country_id': jordan.id if jordan else False,
        }
        if partner:
            partner.write(vals)
        else:
            vals['customer_rank'] = 1
            partner = Partner.create(vals)

        order = SaleOrder.create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': line['product'].product_variant_id.id,
                'product_uom_qty': line['qty'],
                'price_unit': line['product'].list_price,
                'name': line['product'].name,
            }) for line in lines],
            'delivery_customer_name': name,
            'delivery_phone': phone,
            'delivery_address': address,
            'delivery_city': city,
            'tz_delivery_status': 'pending',
            'payment_method_cod': True,
            'note': '%s | %s | %s | %s | COD' % (
                name, phone, address, city_labels.get(city, city),
            ),
            'origin': 'Torque Zone Shop',
        })
        order.action_confirm()
        request.session['torque_cart'] = {'lines': []}

        return request.render('torque_zone_shop.shop_confirmation', self._page_ctx(
            'cart',
            order=order,
            city_label=self._city_labels().get(city, city),
            address_label=address,
            journey_step='done',
        ))

    @http.route('/shop/cart/count', type='json', auth='public', website=True)
    def shop_cart_count_json(self):
        return {'count': self._cart_count()}
