# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


INDONESIAN_MONTHES = {
	1: 'Januari',
	2: 'Februari',
	3: 'Maret',
	4: 'April',
	5: 'Mei',
	6: 'Juni',
	7: 'Juli',
	8: 'Agustus',
	9: 'September',
	10: 'Oktober',
	11: 'Nopember',
	12: 'Desember',    
}

class rekapitulasi_kontrak(models.Model):
	_inherit = 'sale.order'

	contract_id = fields.Many2one('project.project','Project Name')
	sale_charge_id = fields.Many2one('sale.charge.config', 'Sale Charge Config', readonly=True, required=True,
									 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	project_code = fields.Char(string='Project Code', readonly=True)
	start_date = fields.Date(string='Start Date', required=True)
	end_date = fields.Date(string='End Date', required=True)
	payment_term = fields.Selection([('15 hari', '15 Hari'), ('akhir bulan', 'Akhir Bulan')], string='Payment Term')
	percent_dp = fields.Float(string='% Down Payment')
	nilai_dp = fields.Integer(string='Nilai Down Payment')
	percent_retensi = fields.Float(string='% Retensi')
	other = fields.Char(string='Other')
	currency_id = fields.Many2one('res.currency',string='Currency')
	amandement = fields.Boolean(string='Amandement')
	partner_id = fields.Many2one('res.partner')
	contract_no = fields.Many2one('sale.order',string='Contract No')
	harga_satuan = fields.Integer('Harga Satuan', required=True, default=1)
	total_harga = fields.Float(string='Total Harga', compute='_compute_harga', store=True)
	tax = fields.Float(string="Tax", default=1)
	freight_charge = fields.Float('Total', compute='_compute_freight_charge', onchange='_fill_orderline',
								  store=True)
	state = fields.Selection([
		('draft', 'Draft'),
		('sent', 'Draft Sent'),
		('sale', 'Confirm'),
		('done', 'Approved'),
		('cancel', 'Cancelled'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

class custom_sale_order(models.Model):
	_inherit = 'sale.order.line'

	uraian = fields.Char(string='Uraian')
	no_task = fields.Char(string="No. Task")
	keterangan = fields.Text(string='Keterangan')
	weight = fields.Integer('Weight', readonly=True, default=1)
	start_date = fields.Date(string='Start Date')
	end_date = fields.Date(string='End Date')

class monitoring_progress(models.Model):
	_name = 'monitoring.progress'

	contract_id = fields.Many2one('sale.order', string='Contract No', required=True)
	name = fields.Char(string="Reference", default='/', readonly=True)
	partner_id = fields.Many2one('sale.order', string='Customer Name', track_visibility='onchange')
	partner_invoice_id = fields.Many2one('sale.order', string='Customer Address', track_visibility='onchange')
	project_name_id = fields.Many2one('sale.order', string='Project Name', track_visibility='onchange')
	revenue_date = fields.Date(string='Revenue Date', required=True)
	currency_id = fields.Char(string='Currency')
	tp_aktual = fields.Float(string='Total Progress Aktual (%)')
	ap_aktual = fields.Float(string='Akumulasi Progress Aktual (%)')
	tp_approved = fields.Float(string='Total Progress Approved (%)')
	ap_approved = fields.Float(string='Akumulasi Progress Approved (%)')
	detail_line = fields.One2many('monitoring.detail','detail_id')
	description = fields.Text(string='Description')
	total_amount = fields.Integer(string='Total')
	progress_line = fields.One2many('account.invoice', 'progress_id')
	description = fields.Text(string="Description")
	state = fields.Selection([
		('new', 'New'),
		('recognize', 'Recognize Revenue'),
		('billing', 'Billing'),
		], string='Status', readonly=True, copy=False, default='new', track_visibility='onchange')

	@api.model
	def create(self, vals):
		seq = self.env['ir.sequence'].next_by_code('contract.monitoring') or '/'
		vals['name'] = seq
		return super(monitoring_progress, self).create(vals)

class monitoring_detail(models.Model):
	_name = 'monitoring.detail'

	detail_id = fields.Many2one('detail_line','Detail')
	no_task = fields.Char(string='No. Task')
	work_description = fields.Char(string='Work Description')
	unit_price = fields.Integer(string='Unit Price')
	progress_date = fields.Date(string='Progress to Date')
	pp_aktual = fields.Float(string='% Progress Aktual')
	pp_approved = fields.Float(string='% Progress Approved')
	total_revenue = fields.Integer(string='Total Revenue')
	total_invoice = fields.Integer(string='Total Invoice')

class form_invoice(models.Model):
	_inherit = 'account.invoice'

	progress_id = fields.Many2one('monitoring.progress', string='No.Progress Report', required=True)
	no_contract = fields.Many2one('sale.order', string='Contract No')
	project_name = fields.Char(string='Project Name')
	tanggal_invoice = fields.Date(string='Tanggal Invoice')
	nilai_tender = fields.Float(string='Nilai Contract')
	user_id = fields.Many2one('res.users',string='Sales Person')
	uang_muka = fields.Float(string='Uang Muka')
	proporsional_dp = fields.Boolean(string='Uang Muka Proporsional')
	retensi = fields.Float(string='Retensi')
	proporsional_retensi = fields.Boolean(string='Retensi Proporsional')
	no_kwitansi = fields.Char(string='No. Kwitansi')
	tanggal_kwitansi = fields.Date(string='Tanggal Kwitansi')
	no_faktur = fields.Char(string='No Faktur')
	tanggal_faktur = fields.Date(string='Tanggal Faktur')
	# amount_terbilang = fields.Char('Terbilang', compute='_get_terbilang')

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
	@api.depends('date_invoice', 'date_due', 'tanggal_faktur', 'tanggal_kwitansi')
	def _get_custom_date_format(self):
		for inv in self:
			if inv.date_invoice:
				self.date_invoice_custom = self._format_local_date(inv.date_invoice)
			if inv.date_due:
				self.date_due_custom = self._format_local_date(inv.date_due)

	# @api.multi
	# def _get_terbilang(self):
	# 	result = {}
	# 	for row in self:
	# 		temp = row.terbilang(int(row.amount))
	# 		result.update({row.id:temp})
	# 	self.amount_terbilang = temp + " Rupiah"

	def terbilang(self, satuan):
		huruf = ["","Satu","Dua","Tiga","Empat","Lima","Enam","Tujuh","Delapan","Sembilan","Sepuluh","Sebelas"]
		hasil = ""; 
		if satuan < 12: 
			hasil = hasil + huruf[satuan]; 
		elif satuan < 20: 
			hasil = hasil + self.terbilang(satuan-10)+" Belas"; 
		elif satuan < 100:
			hasil = hasil + self.terbilang(satuan/10)+" Puluh "+self.terbilang(satuan%10); 
		elif satuan < 200: 
			hasil=hasil+"Seratus "+self.terbilang(satuan-100); 
		elif satuan < 1000: 
			hasil=hasil+self.terbilang(satuan/100)+" Ratus "+self.terbilang(satuan%100); 
		elif satuan < 2000: 
			hasil=hasil+"Seribu "+self.terbilang(satuan-1000); 
		elif satuan < 1000000: 
			hasil=hasil+self.terbilang(satuan/1000)+" Ribu "+self.terbilang(satuan%1000); 
		elif satuan < 1000000000:
			hasil=hasil+self.terbilang(satuan/1000000)+" Juta "+self.terbilang(satuan%1000000);
		elif satuan < 1000000000000:
			hasil=hasil+self.terbilang(satuan/1000000000)+" Milyar "+self.terbilang(satuan%1000000000)
		elif satuan >= 1000000000000:
			hasil="Angka terlalu besar, harus kurang dari 1 Trilyun!"; 
		return hasil;   

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
	progress_date = fields.Date(string='Progress Date')
	progress_aktual = fields.Float(string='Progress Aktual')
	progress_approved = fields.Float(string='Progress Approved')
	tax = fields.Float(string='Tax')
	nilai_invoice = fields.Float(string='Nilai Invoice')