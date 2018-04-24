# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sti_company(models.Model):
	_inherit = 'res.company'

	company_id = fields.Many2one('res.company')
	user_id = fields.Many2one('res.users','Director Name', required=True)

class sti_customer(models.Model):
	_inherit = 'res.partner'

	partner_id = fields.Many2one('res.partner')
	npwp = fields.Char('NPWP')

