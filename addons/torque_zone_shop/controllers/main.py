# -*- coding: utf-8 -*-
import json

from odoo import http, _
from odoo.http import request

from odoo.addons.torque_zone_shop.const import JORDAN_CITIES, JORDAN_CITIES_AR, UI_STRINGS


class TorqueZoneShop(http.Controller):

    # ── Session / cart helpers ──────────────────────────────────────────

    def _get_cart(self):
        return request.session.get('torque_cart', {'lines': []})

    def _save_cart(self, cart):
        request.session['torque_cart'] = cart
        request.session.modified = True

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

    def _ui(self):
        lang = 'ar' if self._is_rtl() else 'en'
        return UI_STRINGS[lang]

    def _page_ctx(self, active_page, **extra):
        ctx = {
            'cart_count': self._cart_count(),
            'active_page': active_page,
            'is_rtl': self._is_rtl(),
            'ui': self._ui(),
            'jordan_cities': self._get_jordan_cities(),
            'nav_categories': self._get_nav_categories(),
            'category_id': extra.get('category_id'),
        }
        ctx.update(extra)
        return ctx

    def _lang_path(self, path):
        if not path.startswith('/'):
            path = '/' + path
        try:
            return request.env['ir.http']._url_for(path)
        except Exception:
            return path

    def _redirect(self, path, **kw):
        target = self._lang_path(kw.get('redirect', path))
        return request.redirect(target, code=303)

    def _get_sort_order(self, sort=''):
        orders = {
            'price_desc': 'list_price desc, name',
            'price_asc': 'list_price asc, name',
            'name': 'name asc',
        }
        return orders.get(sort, 'name asc')

    def _search_shop_products(self, category_id=None, search='', sort='', page=1):
        Product = request.env['product.template'].sudo()
        domain = self._get_products_domain(category_id)
        if search:
            domain.append(('name', 'ilike', search))
        limit = 24
        offset = (page - 1) * limit
        products = Product.search(domain, order=self._get_sort_order(sort), limit=limit, offset=offset)
        total = Product.search_count(domain)
        return products, total, max(1, (total + 23) // 24)

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

    def _get_product_images(self, product):
        images = []
        if product.image_512:
            images.append({
                'id': 'main',
                'url': f'/web/image/product.template/{product.id}/image_512',
                'name': product.name,
            })
        extra_media = getattr(product, 'product_template_image_ids', None)
        if extra_media:
            for media in extra_media.sorted('sequence'):
                if media.image_512:
                    images.append({
                        'id': media.id,
                        'url': f'/web/image/product.image/{media.id}/image_512',
                        'name': media.name or product.name,
                    })
        if not images:
            images.append({
                'id': 'placeholder',
                'url': '/torque_zone_shop/static/src/img/placeholder.svg',
                'name': product.name,
            })
        return images

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

    def _category_product_count(self, category):
        return request.env['product.template'].sudo().search_count(
            self._get_products_domain(category.id),
        )

    def _get_nav_categories(self):
        Category = request.env['product.category'].sudo()
        roots = Category.search([('parent_id', '=', False)], order='name')
        nav = []
        for root in roots:
            children = Category.search([('parent_id', '=', root.id)], order='name')
            visible_children = [c for c in children if self._category_product_count(c) > 0]
            if self._category_product_count(root) > 0 or visible_children:
                nav.append({'category': root, 'children': visible_children})
        return nav

    def _get_categories(self):
        Category = request.env['product.category'].sudo()
        roots = Category.search([('parent_id', '=', False)], order='name')
        return Category.browse([
            root.id for root in roots if self._category_product_count(root) > 0
        ])

    def _get_filter_categories(self, category_id=None):
        Category = request.env['product.category'].sudo()
        if category_id:
            cat = Category.browse(int(category_id))
            if cat.exists():
                children = Category.search([('parent_id', '=', cat.id)], order='name')
                visible = [c for c in children if self._category_product_count(c) > 0]
                if visible:
                    return visible
        return self._get_categories()

    # ── Website pages ───────────────────────────────────────────────────

    @http.route(['/', '/home'], type='http', auth='public', website=True, sitemap=True)
    def page_home(self, **kw):
        Product = request.env['product.template'].sudo()
        domain = self._get_products_domain()
        featured = Product.search(domain, order='write_date desc', limit=8)
        categories = self._get_categories()
        category_items = [
            {'category': cat, 'count': self._category_product_count(cat)}
            for cat in categories
        ]
        return request.render('torque_zone_shop.page_home', self._page_ctx(
            'home', featured_products=featured, categories=category_items,
        ))

    @http.route('/about', type='http', auth='public', website=True, sitemap=True)
    def page_about(self, **kw):
        return request.render('torque_zone_shop.page_about', self._page_ctx('about'))

    @http.route('/contact', type='http', auth='public', website=True)
    def page_contact_redirect(self, **kw):
        return request.redirect(self._lang_path('/'))

    # ── Shop ────────────────────────────────────────────────────────────

    @http.route(['/shop', '/shop/page/<int:page>'], type='http', auth='public', website=True)
    def shop_catalog(self, page=1, search='', sort='', category_id=None, **kw):
        products, total, total_pages = self._search_shop_products(
            category_id=category_id, search=search, sort=sort, page=page,
        )
        return request.render('torque_zone_shop.shop_catalog', self._page_ctx(
            'shop',
            products=products,
            categories=self._get_filter_categories(category_id),
            search=search,
            sort=sort or 'name',
            category_id=int(category_id) if category_id else None,
            page=page,
            total_pages=total_pages,
            product_total=total,
        ))

    @http.route('/shop/category/<int:category_id>', type='http', auth='public', website=True)
    def shop_category(self, category_id, page=1, search='', sort='', **kw):
        category = request.env['product.category'].sudo().browse(category_id)
        if not category.exists():
            return request.redirect(self._lang_path('/shop'))

        products, total, total_pages = self._search_shop_products(
            category_id=category_id, search=search, sort=sort, page=page,
        )
        return request.render('torque_zone_shop.shop_catalog', self._page_ctx(
            'shop',
            products=products,
            categories=self._get_filter_categories(category_id),
            category=category,
            search=search,
            sort=sort or 'name',
            category_id=category_id,
            page=page,
            total_pages=total_pages,
            product_total=total,
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

        images = self._get_product_images(product)
        return request.render('torque_zone_shop.shop_product', self._page_ctx(
            'shop',
            product=product,
            related_products=related,
            images=images,
            image_url=images[0]['url'],
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
            if int(line['product_id']) == product.id:
                line['qty'] += qty
                break
        else:
            cart['lines'].append({'product_id': product.id, 'qty': qty})
        self._save_cart(cart)
        if kw.get('ajax'):
            return self._json_response(self._cart_json_state())
        return self._redirect('/shop/cart', **kw)

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
        return self._redirect('/shop/cart')

    def _format_money(self, currency, amount):
        if hasattr(currency, 'format'):
            return currency.format(amount)
        return '%.2f' % amount

    def _cart_json_state(self, product_id=None):
        cart = self._get_cart()
        lines = self._enrich_cart_lines(cart)
        currency = (
            lines[0]['product'].currency_id if lines
            else request.env.company.currency_id
        )
        line_data = None
        if product_id is not None:
            pid = int(product_id)
            match = next((l for l in lines if l['product_id'] == pid), None)
            if match:
                line_data = {
                    'product_id': pid,
                    'qty': match['qty'],
                    'subtotal': match['subtotal'],
                    'subtotal_formatted': self._format_money(currency, match['subtotal']),
                    'removed': False,
                }
            else:
                line_data = {'product_id': pid, 'qty': 0, 'removed': True}

        return {
            'count': self._cart_count(),
            'total': sum(l['subtotal'] for l in lines),
            'total_formatted': self._format_money(currency, sum(l['subtotal'] for l in lines)),
            'empty': not lines,
            'line': line_data,
        }

    def _json_response(self, data):
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
        )

    def _adjust_cart_qty(self, product_id, action):
        pid = int(product_id)
        cart = self._get_cart()
        new_lines = []
        changed = False
        for line in cart.get('lines', []):
            if int(line.get('product_id', 0)) != pid:
                new_lines.append(line)
                continue
            qty = int(line.get('qty', 1))
            if action == 'inc':
                line['qty'] = qty + 1
                new_lines.append(line)
                changed = True
            elif action == 'dec':
                if qty <= 1:
                    changed = True
                    continue
                line['qty'] = qty - 1
                new_lines.append(line)
                changed = True
            else:
                new_lines.append(line)
        if changed:
            cart['lines'] = new_lines
            self._save_cart(cart)

    @http.route('/shop/cart/update_qty', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def shop_cart_update_qty(self, product_id, action='inc', **kw):
        self._adjust_cart_qty(product_id, action)
        return self._json_response(self._cart_json_state(product_id))

    @http.route('/shop/cart/remove_item', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def shop_cart_remove_item(self, product_id, **kw):
        cart = self._get_cart()
        cart['lines'] = [
            l for l in cart.get('lines', [])
            if int(l['product_id']) != int(product_id)
        ]
        self._save_cart(cart)
        return self._json_response(self._cart_json_state(product_id))

    @http.route('/shop/cart/qty', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def shop_cart_qty(self, product_id, action='inc', **kw):
        self._adjust_cart_qty(product_id, action)
        return self._redirect('/shop/cart', **kw)

    @http.route('/shop/cart/inc/<int:product_id>', type='http', auth='public', website=True)
    def shop_cart_inc(self, product_id, **kw):
        self._adjust_cart_qty(product_id, 'inc')
        return self._redirect('/shop/cart', **kw)

    @http.route('/shop/cart/dec/<int:product_id>', type='http', auth='public', website=True)
    def shop_cart_dec(self, product_id, **kw):
        self._adjust_cart_qty(product_id, 'dec')
        return self._redirect('/shop/cart', **kw)

    @http.route('/shop/cart/remove/<int:product_id>', type='http', auth='public', website=True)
    def shop_cart_remove(self, product_id, **kw):
        cart = self._get_cart()
        cart['lines'] = [l for l in cart.get('lines', []) if int(l['product_id']) != int(product_id)]
        self._save_cart(cart)
        return self._redirect('/shop/cart', **kw)

    @http.route('/shop/checkout', type='http', auth='public', website=True)
    def shop_checkout(self, **kw):
        lines = self._enrich_cart_lines(self._get_cart())
        if not lines:
            return self._redirect('/shop/cart')
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
            return self._redirect('/shop/cart')

        name = (post.get('customer_name') or '').strip()
        phone = (post.get('phone_number') or '').strip()
        address = (post.get('address') or '').strip()
        city = (post.get('city') or '').strip()
        city_labels = dict(JORDAN_CITIES)

        errors = []
        ui = self._ui()
        if not name:
            errors.append(ui['err_name'])
        if not phone:
            errors.append(ui['err_phone'])
        if not address:
            errors.append(ui['err_address'])
        if not city or city not in city_labels:
            errors.append(ui['err_city'])

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
        self._save_cart({'lines': []})

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
