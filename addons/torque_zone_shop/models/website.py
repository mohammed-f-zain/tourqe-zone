# -*- coding: utf-8 -*-
from odoo import api, models


class Website(models.Model):
    _inherit = 'website'

    def sale_get_order(self, force_create=False):
        """Torque Zone uses session torque_cart — ignore Odoo draft sale orders."""
        return self.env['sale.order']

    @api.model
    def tz_configure_languages(self):
        """Set Arabic as default website language on upgrade."""
        ar = self.env.ref('base.lang_ar')
        en = self.env.ref('base.lang_en')
        ar.sudo().write({'active': True})
        en.sudo().write({'active': True})
        for website in self.sudo().search([]):
            website.write({
                'default_lang_id': ar.id,
                'language_ids': [(6, 0, [ar.id, en.id])],
            })
