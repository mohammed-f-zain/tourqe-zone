# -*- coding: utf-8 -*-
"""
Override Odoo's default website_sale /shop routes so our custom
Torque Zone storefront is always used.
"""
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

        @http.route([
            '/shop/cart',
        ], type='http', auth='public', website=True, sitemap=False)
        def cart(self, **post):
            return _shop.shop_cart(**post)

        @http.route([
            '/shop/checkout',
        ], type='http', auth='public', website=True, sitemap=False)
        def checkout(self, **post):
            return _shop.shop_checkout(**post)
