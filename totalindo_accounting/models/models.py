# -*- coding: utf-8 -*-

from odoo import models, fields, api

class journal_project(models.Model):
	_name = 'journal.project'

	name = fields.Char(string="Reference", default='/', readonly=True)
	revenue = fields.Many2one('account.account','Revenue')
	beban_pajak = fields.Many2one('account.account','Beban Pajak')
	pph_4_2 = fields.Many2one('account.tax', string='Pajak PPH Pasal 4 (2)', domain=['|', ('active', '=', False), ('active', '=', True)])
	piutang_bruto = fields.Many2one('account.account','Piutang Bruto')
	ar_retensi = fields.Many2one('account.account','AR Retensi')
	uang_muka = fields.Many2one('account.account','Uang Muka')
	ppn_keluaran = fields.Many2one('account.account','PPN Keluaran')
	cogs = fields.Many2one('account.account','COGS')
	wip_cogs = fields.Many2one('account.account','WIP')
	accrued_biaya = fields.Many2one('account.account','Accrued Biaya')
	# accrued_biaya = fields.Many2one('account.account','Accrued Biaya', domain=[('is_journal_project', '=', True)])

	@api.model
	def create(self, vals):
		seq = self.env['ir.sequence'].next_by_code('account.journal') or '/'
		vals['name'] = seq
		return super(journal_project, self).create(vals)

class account_inherit(models.Model):
	_inherit = 'account.account'

	is_journal_project = fields.Boolean('Is Journal Project')