# -*- coding: utf-8 -*-

from odoo import models, fields, api

class journal_project(models.Model):
	_name = 'journal.project'

	account_id = fields.Many2one('account.account')
	wip_pengakuan = fields.Char('WIP Pendapatan', domain=[('is_journal_project', '=', True)])
	revenue = fields.Char('Revenue')
	beban_pajak = fields.Char('Beban Pajak')
	pph_4_2 = fields.Char('Pajak PPh Pasal 4(2)')
	piutang_bruto = fields.Char('Piutang Bruto')
	ar_retensi = fields.Char('AR Retensi')
	uang_muka = fields.Char('Uang Muka')
	ppn_keluaran = fields.Char('PPN Keluaran')
	cogs = fields.Char('COGS')
	wip_cogs = fields.Char('WIP COGS')
	accrued_biaya = fields.Char('Accrued Biaya')

class account_inherit(models.Model):
	_inherit = 'account.account'

	is_journal_project = fields.Boolean('Is Journal Project')