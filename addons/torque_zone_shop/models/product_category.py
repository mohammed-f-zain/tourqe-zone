# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    tz_website_description = fields.Text(
        string='Website Description',
        translate=True,
        help='Short description shown on the shop category page (translate per language).',
    )
