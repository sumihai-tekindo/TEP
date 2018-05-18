# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    pmdir_treshhold_amount = fields.Monetary(related='company_id.pmdir_treshhold_amount',
                                             string='SPK Treshhold amount', currency_field='company_currency_id')


class Company(models.Model):
    _inherit = 'res.company'
    
    pmdir_treshhold_amount = fields.Monetary(string='SPK Treshhold amount')
