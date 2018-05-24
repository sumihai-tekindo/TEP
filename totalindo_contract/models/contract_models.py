# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.totalindo_report import terbilang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import odoo.addons.decimal_precision as dp


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

class SaleOrder(models.Model):
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
	amandement = fields.Selection([('tambah', 'Tambah'), ('kurang', 'Kurang')], string='Amandement')
	partner_id = fields.Many2one('res.partner')
	contract_no = fields.Many2one('sale.order',string='Contract No')
	harga_satuan = fields.Integer('Harga Satuan', required=True, default=1)
	tax = fields.Float(string="Tax", default=1)
	state = fields.Selection([
		('draft', 'Draft'),
		('sent', 'Draft Sent'),
		('sale', 'Confirm'),
		('done', 'Approved'),
		('cancel', 'Cancelled'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('so.sequence.inherit') or '/'
			code = self.env['project.project'].browse(vals['contract_id']).code
			vals['name'] = vals['name'][:10]+'/TEP-'+code+vals['name'][10:]
		return super(SaleOrder, self).create(vals)

class custom_sale_order(models.Model):
	_inherit = 'sale.order.line'

	uraian = fields.Char(string='Uraian')
	no_task = fields.Char(string="No. Task")
	keterangan = fields.Text(string='Keterangan')
	weight = fields.Float('Weight', readonly=True, compute='_compute_weight', digits=dp.get_precision('Discount'), default=0.0)
	start_date = fields.Date(string='Start Date')
	end_date = fields.Date(string='End Date')

	@api.depends('weight','product_uom_qty', 'price_unit')
	def _compute_weight(self):
		for record in self:
			if record.order_id.amount_untaxed != 0 and record.price_unit != 0 and record.product_uom_qty != 0:
				record.weight = record.product_uom_qty * record.price_unit / record.order_id.amount_untaxed * 100

class monitoring_progress(models.Model):
	_name = 'monitoring.progress'

	contract_id = fields.Many2one('sale.order', string='Contract No', required=True)
	name = fields.Char(string="Reference", default='/', readonly=True)
	partner_id = fields.Many2one('res.partner', string='Customer Name', track_visibility='onchange')
	partner_invoice_id = fields.Many2one('res.partner', string='Customer Address', track_visibility='onchange')
	project_name_id = fields.Many2one('project.project', string='Project Name', track_visibility='onchange')
	revenue_date = fields.Date(string='Revenue Date', required=True)
	currency_id = fields.Many2one("res.currency", readonly=True)
	tp_aktual = fields.Float(string='Total Progress Aktual (%)')
	ap_aktual = fields.Float(string='Akumulasi Progress Aktual (%)')
	tp_approved = fields.Float(string='Total Progress Approved (%)', related='detail_line.pp_approved', store=True)
	ap_approved = fields.Float(string='Akumulasi Progress Approved (%)')
	detail_line = fields.One2many('monitoring.detail','monitoring_progress_id')
	description = fields.Text(string='Description')
	total_amount = fields.Integer(string='Total')
	progress_line = fields.One2many('account.invoice', 'progress_id')
	state = fields.Selection([
		('new', 'New'),
		('recognize', 'Recognize Revenue'),
		('approve', 'Customer Approved'),
		('billing', 'Billing'),
		], string='Status', readonly=True, copy=False, default='new', track_visibility='onchange')
	note = fields.Text(string="Description")
	amount_total = fields.Float(string="Total", readonly=True)

	@api.onchange('contract_id')
	def monitoring_contract(self):
		self.partner_id = self.contract_id.partner_id.id
		self.partner_invoice_id = self.contract_id.partner_invoice_id.id
		self.project_name_id = self.contract_id.contract_id.id
		self.currency_id = self.contract_id.currency_id.id

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('contract.monitoring') or '/'
			code = self.env['project.project'].browse(vals['project_name_id']).code
			vals['name'] = vals['name'][:10]+'/TEP-'+code+vals['name'][10:]
		return super(monitoring_progress, self).create(vals)

	@api.multi
	def generate_progress(self):
		self.write({'state': 'new'})
		for monitoring in self:
			project_id = monitoring.project_name_id and monitoring.project_name_id.id or False
			project_start_date = monitoring.project_name_id.date_from
			if not project_start_date:
				raise ValidationError(_('You cannot generate progress due to start date in project is undefined!'))
			dt_project_start_date = datetime.strptime(project_start_date,'%Y-%m-%d')
			dt_revenue_date = datetime.strptime(monitoring.revenue_date,'%Y-%m-%d')
			dt_delta_date = dt_revenue_date-dt_project_start_date
			monitoring_id =monitoring.id or False
			if project_id:
				if monitoring.detail_line:
					monitoring.detail_line.unlink()

				task_ids = self.env['project.task'].search([('project_id','=',project_id)])
				header_total_percentage = 0.0
				for task in task_ids:
					t_temp = {
						'monitoring_progress_id': monitoring_id,
						'no_task': task.name or '/',
						'task_id': task.id,
						# 'work_description': task.progress_ids.name,
						'unit_price': task.amount,
						'progress_date': dt_delta_date.days,
						'pp_aktual': task.progress_actual,
						'pp_approved': False,
						'total_revenue': task.progress_actual/100.0 * task.amount,
						'total_invoice': 0.0,
						}
					x = self.env['monitoring.detail'].new(t_temp)

					for progress in task.progress_ids:
						t_temp.update(dict(x._convert_to_write(x._cache),work_description=progress.name))
						self.env['monitoring.detail'].create(t_temp)
					header_total_percentage+=task.progress_actual
				monitoring.tp_aktual = header_total_percentage

	@api.multi
	def recalculate_progress(self):
		self.write({'state': 'recognize'})
		for monitoring in self:
			project_id = monitoring.project_name_id and monitoring.project_name_id.id or False
			project_start_date = monitoring.project_name_id.date_from
			if not project_start_date:
				raise ValidationError(_('You cannot generate progress due to start date in project is undefined!'))
			dt_project_start_date = datetime.strptime(project_start_date,'%Y-%m-%d')
			dt_revenue_date = datetime.strptime(monitoring.revenue_date,'%Y-%m-%d')
			dt_delta_date = dt_revenue_date-dt_project_start_date
			detail_id = monitoring.id
			header_total_percentage = 0.0
			for line in monitoring.detail_line:
				task = line.task_id
				t_temp = {
						'monitoring_progress_id': detail_id,
						'no_task': task.name or '/',
						'task_id': task.id,
						'work_description': task.progress_ids.name,
						'unit_price': task.amount,
						'progress_date': dt_delta_date.days,
						'pp_aktual': task.progress_actual,
						'pp_approved': False,
						'total_revenue': task.progress_actual/100.0 * task.amount,
						'total_invoice': 0.0,
						}
				line.write(t_temp)
				header_total_percentage+=task.progress_actual
			monitoring.tp_aktual = header_total_percentage
			
	@api.multi
	def recognize_revenue(self):
		self.write({'state': 'approve'})

	@api.multi
	def customer_approved(self):
		self.write({'state': 'billing'})

	@api.multi
	def generate_billing(self):
		self.write({'state': 'recognize'})

class monitoring_detail(models.Model):
	_name = 'monitoring.detail'
	_rec_name = 'no_task'

	monitoring_progress_id = fields.Many2one('monitoring.progress','Detail')
	no_task = fields.Char(string='No. Task')
	task_id = fields.Many2one('project.task',"Related Task")
	task_description = fields.Char(string='Task Name')
	unit_price = fields.Integer(string='Unit Price')
	progress_date = fields.Integer(string='Progress to Date')
	pp_aktual = fields.Float(string='% Progress Aktual')
	pp_approved = fields.Float(string='% Progress Approved')
	total_revenue = fields.Integer(string='Total Revenue')
	total_invoice = fields.Integer(string='Total Invoice', compute="_compute_invoice")
	state = fields.Selection(related='monitoring_progress_id.state', store=True, default='new')

	@api.depends('total_invoice','unit_price', 'pp_approved')
	def _compute_invoice(self):
		for record in self:
			if record.unit_price != 0 and record.pp_approved != 0:
				record.total_invoice = record.unit_price * record.pp_approved/100

	# @api.onchange('pp_approved')
	# def _approved_progress(self):
	# 	self.ensure_one()
	# 	self.monitoring_progress_id.tp_approved = self.pp_approved
	# 	print self.monitoring_progress_id.tp_approved

class form_invoice(models.Model):
	_inherit = 'account.invoice'

	progress_id = fields.Many2one('monitoring.progress', string='No.Progress Report')
	no_contract = fields.Many2one('sale.order', string='Contract No')
	project_name_id = fields.Many2one('project.project',string='Project Name')
	tanggal_invoice = fields.Date(string='Tanggal Invoice')
	nilai_tender = fields.Float(string='Nilai Contract')
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
	progress_date = fields.Date(string='Progress Date')
	progress_aktual = fields.Float(string='Progress Aktual')
	progress_approved = fields.Float(string='Progress Approved')
	tax = fields.Float(string='Tax')
	nilai_invoice = fields.Float(string='Nilai Invoice')