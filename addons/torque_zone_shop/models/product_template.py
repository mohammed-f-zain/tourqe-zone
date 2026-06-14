# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    torque_shop_published = fields.Boolean(
        string='Show in Shop',
        default=True,
        help='Display this product on the Torque Zone storefront.',
    )
