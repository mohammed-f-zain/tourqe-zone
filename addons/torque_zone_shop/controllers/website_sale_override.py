# -*- coding: utf-8 -*-
"""Override all Odoo website_sale shop routes with our custom storefront."""
from odoo import http
from odoo.http import request

from odoo.addons.torque_zone_shop.controllers.main import TorqueZoneShop

try:
    from odoo.addons.website_sale.controllers.main import WebsiteSale
except ImportError:
    WebsiteSale = None

_shop = TorqueZoneShop()


if WebsiteSale:

    class TorqueZoneWebsiteSale(WebsiteSale):

        @http.route([
            '/shop',
            '/shop/page/<int:page>',
            '/shop/category/<int:category_id>',
            '/shop/category/<int:category_id>/page/<int:page>',
        ], type='http', auth='public', website=True, sitemap=True)
        def shop(self, page=1, category_id=None, search='', **post):
            search = search or post.get('search', '')
            if category_id:
                return _shop.shop_category(category_id, page=page, search=search, **post)
            return _shop.shop_catalog(page=page, search=search, category_id=None, **post)

        @http.route([
            '/shop/<model("product.template"):product>',
        ], type='http', auth='public', website=True, sitemap=True)
        def product(self, product, category='', search='', **kwargs):
            if not getattr(product, 'torque_shop_published', False) or not product.sale_ok:
                return request.redirect('/shop')
            return _shop.shop_product(product.id, **kwargs)

        @http.route('/shop/cart', type='http', auth='public', website=True, sitemap=False)
        def cart(self, **post):
            return _shop.shop_cart(**post)

        @http.route('/shop/cart/add', type='http', auth='public', methods=['POST'], website=True, csrf=True)
        def cart_add(self, product_id, qty=1, **kw):
            return _shop.shop_cart_add(product_id, qty=qty, **kw)

        @http.route('/shop/cart/update_qty', type='http', auth='public', methods=['POST'], website=True, csrf=True)
        def cart_update_qty(self, product_id, action='inc', **kw):
            return _shop.shop_cart_update_qty(product_id, action=action, **kw)

        @http.route('/shop/cart/qty', type='http', auth='public', methods=['POST'], website=True, csrf=True)
        def cart_qty(self, product_id, action='inc', **kw):
            return _shop.shop_cart_qty(product_id, action=action, **kw)

        @http.route('/shop/cart/inc/<int:product_id>', type='http', auth='public', website=True)
        def cart_inc(self, product_id, **kw):
            return _shop.shop_cart_inc(product_id, **kw)

        @http.route('/shop/cart/dec/<int:product_id>', type='http', auth='public', website=True)
        def cart_dec(self, product_id, **kw):
            return _shop.shop_cart_dec(product_id, **kw)

        @http.route('/shop/cart/update', type='http', auth='public', methods=['POST'], website=True, csrf=True)
        def cart_update(self, **post):
            return _shop.shop_cart_update(**post)

        @http.route('/shop/cart/remove_item', type='http', auth='public', methods=['POST'], website=True, csrf=True)
        def cart_remove_item(self, product_id, **kw):
            return _shop.shop_cart_remove_item(product_id, **kw)

        @http.route('/shop/cart/remove/<int:product_id>', type='http', auth='public', website=True)
        def cart_remove(self, product_id, **kw):
            return _shop.shop_cart_remove(product_id, **kw)

        @http.route('/shop/checkout', type='http', auth='public', website=True, sitemap=False)
        def checkout(self, **post):
            return _shop.shop_checkout(**post)

        @http.route('/shop/order/confirm', type='http', auth='public', methods=['POST'], website=True, csrf=True)
        def order_confirm(self, **post):
            return _shop.shop_order_confirm(**post)

        @http.route('/shop/payment', type='http', auth='public', website=True)
        def shop_payment(self, **post):
            return request.redirect('/shop/checkout')

        @http.route('/shop/confirmation', type='http', auth='public', website=True)
        def shop_payment_confirmation(self, **post):
            return request.redirect('/shop')
