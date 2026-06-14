# -*- coding: utf-8 -*-
from odoo import api, fields, models

from odoo.addons.torque_zone_shop.const import DELIVERY_STATUSES, JORDAN_CITIES


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tz_delivery_status = fields.Selection(
        DELIVERY_STATUSES,
        string='Delivery Status',
        default='pending',
        tracking=True,
        copy=False,
    )
    delivery_city = fields.Selection(
        JORDAN_CITIES,
        string='Delivery City',
        tracking=True,
    )
    delivery_customer_name = fields.Char(string='Customer Name')
    delivery_phone = fields.Char(string='Phone Number')
    payment_method_cod = fields.Boolean(
        string='Cash on Delivery',
        default=True,
        readonly=True,
    )

    @api.model
    def _get_jordan_country(self):
        return self.env.ref('base.jo', raise_if_not_found=False)

    def action_delivery_confirm(self):
        self.filtered(lambda o: o.tz_delivery_status == 'pending').write({
            'tz_delivery_status': 'confirmed',
        })

    def action_delivery_prepare(self):
        self.write({'tz_delivery_status': 'preparing'})

    def action_delivery_ship(self):
        self.write({'tz_delivery_status': 'out_for_delivery'})

    def action_delivery_complete(self):
        self.write({'tz_delivery_status': 'delivered'})

    def action_delivery_cancel(self):
        self.write({'tz_delivery_status': 'cancelled'})
