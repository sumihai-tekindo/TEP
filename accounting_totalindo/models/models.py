# -*- coding: utf-8 -*-

from odoo import models, fields, api

class journal_project(models.Model):
	_name = 'journal.project'

	name = fields.Char(string="Reference", default='/', readonly=True)
	wip_pengakuan = fields.Many2one('account.account','WIP Pendapatan')
	revenue = fields.Many2one('account.account','Revenue', domain=[('is_journal_project', '=', True)])
	beban_pajak = fields.Many2one('account.account','Beban Pajak', domain=[('is_journal_project', '=', True)])
	pph_4_2 = fields.Many2one('account.account','Pajak PPh Pasal 4(2)', domain=[('is_journal_project', '=', True)])
	piutang_bruto = fields.Many2one('account.account','Piutang Bruto', domain=[('is_journal_project', '=', True)])
	ar_retensi = fields.Many2one('account.account','AR Retensi', domain=[('is_journal_project', '=', True)])
	uang_muka = fields.Many2one('account.account','Uang Muka', domain=[('is_journal_project', '=', True)])
	ppn_keluaran = fields.Many2one('account.account','PPN Keluaran', domain=[('is_journal_project', '=', True)])
	cogs = fields.Many2one('account.account','COGS', domain=[('is_journal_project', '=', True)])
	wip_cogs = fields.Many2one('account.account','WIP COGS', domain=[('is_journal_project', '=', True)])
	accrued_biaya = fields.Many2one('account.account','Accrued Biaya', domain=[('is_journal_project', '=', True)])

	@api.model
	def create(self, vals):
		seq = self.env['ir.sequence'].next_by_code('account.journal') or '/'
		vals['name'] = seq
		return super(journal_project, self).create(vals)

class account_inherit(models.Model):
	_inherit = 'account.account'

	is_journal_project = fields.Boolean('Is Journal Project')