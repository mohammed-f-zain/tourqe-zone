# -*- coding: utf-8 -*-
{
    'name': 'Torque Zone Shop',
    'version': '18.0.10.3.0',
    'category': 'Website/Website',
    'summary': 'Full professional website with COD e-commerce for Jordan',
    'description': """
        Complete Torque Zone website: Home, About Us, Shop.
        Cash-on-delivery checkout with Jordan cities and sales delivery tracking.
    """,
    'author': 'Torque Zone',
    'depends': [
        'website',
        'website_sale',
        'sale',
        'sale_stock',
        'stock',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_status_data.xml',
        'data/website_langs.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/product_category_views.xml',
        'views/website_layout.xml',
        'views/website_assets.xml',
        'views/website_chrome.xml',
        'views/journey.xml',
        'views/website_pages.xml',
        'views/shop_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
