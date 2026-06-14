# -*- coding: utf-8 -*-
from odoo import api, models


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def tz_configure_languages(self):
        """Set Arabic default and reload storefront translations on every upgrade."""
        ar = self.env.ref('base.lang_ar')
        en = self.env.ref('base.lang_en')
        ar.sudo().write({'active': True})
        en.sudo().write({'active': True})
        for website in self.sudo().search([]):
            website.write({
                'default_lang_id': ar.id,
                'language_ids': [(6, 0, [ar.id, en.id])],
            })
        module = self.env['ir.module.module'].sudo().search(
            [('name', '=', 'torque_zone_shop'), ('state', '=', 'installed')],
            limit=1,
        )
        if module:
            module._update_translations(['torque_zone_shop'], ['ar_001'])
