# -*- coding: utf-8 -*-

from odoo import models, fields, api

class form_invoice(models.Model):
	_inherit = 'account.invoice'

	progress_id = fields.Many2one('monitoring.progress', string='No.Progress Report')
	no_contract = fields.Many2one('sale.order', string='Contract No')
	project_name_id = fields.Many2one('project.project',string='Project Name')
	tanggal_invoice = fields.Date(string='Tanggal Invoice')
	nilai_tender = fields.Float(string='Total Nilai Contract')
	user_id = fields.Many2one('res.users',string='Sales Person')
	uang_muka = fields.Float(string='Uang Muka')
	proporsional_dp = fields.Boolean(string='Uang Muka Proporsional')
	retensi = fields.Float(string='Retensi')
	proporsional_retensi = fields.Boolean(string='Retensi Proporsional')
	no_kwitansi = fields.Char(string='No. Kwitansi')
	tanggal_kwitansi = fields.Date(string='Tanggal Kwitansi')
	date_kwitansi_custom = fields.Char(compute='_get_custom_date_format', string="Tanggal Kwitansi")
	no_faktur = fields.Char(string='No Faktur')
	tanggal_faktur = fields.Date(string='Tanggal Faktur')
	date_faktur_custom = fields.Char(compute='_get_custom_date_format', string="Tanggal Faktur")
	amount_terbilang = fields.Char('Terbilang', compute='_get_terbilang')

	@api.onchange('progress_id')
	def progress_report(self):
		self.no_contract = self.progress_id.contract_id.id
		self.project_name_id = self.progress_id.project_name_id.id
		self.partner_id = self.progress_id.partner_id.id
		self.nilai_tender = self.progress_id.total_amount
		self.invoice_line_ids.progress_aktual = self.progress_id.tp_aktual
		self.invoice_line_ids.progress_approved = self.progress_id.tp_approved
		# self.invoice_line_ids.progress_date = self.progress_id.detail_line.progress_date
		print "========================progress date==",self.invoice_line_ids.progress_date

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('account.sequence.inherit') or '/'
			code = self.env['project.project'].browse(vals['project_name_id']).code
			vals['name'] = vals['name'][:10]+'/TEP-'+code+vals['name'][10:]
		return super(form_invoice, self).create(vals)

	def _format_local_date(self,dt):
		if not dt:
			return '-'
		elif len(dt)==10:
			FORMAT = DF
		else:
			FORMAT = DTF
		dt = datetime.strptime(dt, FORMAT)
		dd = dt.day
		dm = INDONESIAN_MONTHES[dt.month]
		dy = dt.year
		return '%s %s %s' % (dd,dm,dy)

	@api.multi
	@api.depends('date_kwitansi_custom', 'date_faktur_custom')
	def _get_custom_date_format(self):
		for inv in self:
			if inv.tanggal_kwitansi:
				self.date_kwitansi_custom = self._format_local_date(inv.tanggal_kwitansi)
			if inv.tanggal_faktur:
				self.date_faktur_custom = self._format_local_date(inv.tanggal_faktur)

	@api.multi
	def _get_terbilang(self):
		result = {}
		for row in self:
			temp = terbilang(int(row.amount_total))
			row.amount_terbilang = temp + " Rupiah" 

	@api.multi
	def cetak_kwitansi(self):
		return self.env['report'].get_action(self, 'totalindo_contract.laporan_kwitansi')

	@api.multi
	def cetak_faktur(self):
		return self.env['report'].get_action(self, 'totalindo_contract.laporan_faktur')

class detail_invoice(models.Model):
	_inherit = 'account.invoice.line'

	no_invoice = fields.Char(string='No.')
	work_description = fields.Char(string='Task')
	progress_date = fields.Date(string='Progress To Date')
	progress_aktual = fields.Float(string='Progress Aktual')
	progress_approved = fields.Float(string='Progress Approved')
	tax = fields.Float(string='Tax')
	nilai_invoice = fields.Float(string='Nilai Invoice')

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