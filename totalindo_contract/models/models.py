# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
	task_line = fields.One2many('task.detail','task_id')

	# sale_ids = fields.Many2many('res.partner', column1='contract_id', column2='partner_id', string='Sales')
	state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Draft Sent'),
        ('sale', 'Confirm'),
        ('done', 'Approved'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

class task_detail(models.Model):
	_name = 'task.detail'

	task_id = fields.Many2one('sale.order','Task Detail')
	product_id = fields.Many2one('product.template', string="No. Task")
	uraian = fields.Char(string='Uraian')
	keterangan = fields.Text(string='Keterangan')
	satuan = fields.Integer('Satuan', required=True, default=1)
	quantity = fields.Integer('Qty', default=1, required=True)
	weight = fields.Integer('Weight', required=True, default=1)
	start_date = fields.Date(string='Start Date')
	end_date = fields.Date(string='End Date')
	harga_satuan = fields.Integer('Harga Satuan', required=True, default=1)
	total_harga = fields.Float(string='Total Harga', compute='_compute_harga', store=True)
	tax = fields.Float(string="Tax", default=1)
	freight_charge = fields.Float('Total', compute='_compute_freight_charge', onchange='_fill_orderline',
								  store=True)

	@api.depends('satuan', 'weight', 'harga_satuan')
	def _compute_harga(self):
		for task in self:
			if task.satuan != 0 and task.weight != 0 and task.harga_satuan != 0:
				task.total_harga = task.satuan * task.weight * task.harga_satuan

	@api.depends('total_harga', 'tax')
	def _compute_freight_charge(self):
		for record in self:
			if record.total_harga != 0 and record.tax != 0:
				record.freight_charge = record.total_harga * record.tax

	@api.onchange('freight_charge')
	def _fill_orderline(self):
		vals = {'order_line': []}
		if self.freight_charge <= 0:
			return {'value': vals}
		elif self.freight_charge:
			obj_product_template = self.env['product.template']
			obj_product_product = self.env['product.product']
			freight_product = obj_product_product.search([('is_freight_charge', '=', True)])
			if freight_product:
				for record in self:
					vals['order_line'].append({
						'product_id': freight_product[0].id,
						'name': freight_product[0].name,
						'product_uom_qty': 1,
						'product_uom': freight_product[0].uom_id.id,
						'price_unit': record.freight_charge,
						'tax_id': freight_product[0].taxes_id[0]
					})
					return {'value': vals}
			else:
				obj_product_template.create({
					'name': 'Freight Charge',
					'sale_ok': True,
					'is_freight_charge': True,
					'type': 'service',
					'default_code': 'FC01',
					'purchase_method': 'purchase',
					# 'taxes_id': [],
					# 'supplier_taxes_id': []
				})
				freight_product = obj_product_product.search([('is_freight_charge', '=', True)])
				if freight_product:
					for record in self:
						vals['order_line'].append({
							'product_id': freight_product[0].id,
							'name': freight_product[0].name,
							'product_uom_qty': 1,
							'product_uom': freight_product[0].uom_id.id,
							'price_unit': record.freight_charge,
							'tax_id': freight_product[0].taxes_id[0]
						})
						return {'value': vals}



class monitoring_progress(models.Model):
	_name = 'monitoring.progress'

	contract_id = fields.Many2one('sale.order', string='Contract No', required=True)
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

	# @api.multi
 #    @api.onchange('contract_id')
 #    def onchange_contract_id(self):
 #        if not self.contract_id:
 #            self.update({
 #                'partner_id': False,
 #                'partner_invoice_id': False,
 #                'project_name_id': False,
 #            })
 #            return

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
	detail_line = fields.One2many('detail.invoice','detail_id')

	# @api.multi
 #    def cetak_faktur(self):
 #        return self.env['report'].get_action(self, 'sti_contract.laporan_faktur')
	
class detail_invoice(models.Model):
	_name = 'detail.invoice'

	detail_id = fields.Many2one('account.invoice','Detail')
	no_invoice = fields.Char(string='No.')
	work_description = fields.Char(string='Work Description')
	progress_date = fields.Date(string='Progress Date')
	progress_aktual = fields.Float(string='Progress Aktual')
	progress_approved = fields.Float(string='Progress Approved')
	tax = fields.Float(string='Tax')
	nilai_invoice = fields.Float(string='Nilai Invoice')

