# -*- coding: utf-8 -*-

from odoo import models, fields, api

class rekapitulasi_kontrak(models.Model):
	_inherit = 'sale.order'

	contract_id = fields.Many2one('project.project','Project Name')
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
	# state = fields.Selection([
 #        ('draft', 'Draft'),
 #        ('sent', 'Draft Sent'),
 #        ('sale', 'Confirm'),
 #        ('done', 'Approved'),
 #        ('cancel', 'Cancelled'),
 #    ], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')

class task_detail(models.Model):
	_name = 'task.detail'

	task_id = fields.Many2one('sale.order','Task Detail')
	no_task = fields.Many2one('project.project', string="No. Task")
	uraian = fields.Char(string='Uraian')
	keterangan = fields.Text(string='Keterangan')
	satuan = fields.Integer(string='Satuan')
	quantity = fields.Integer(string='Qty')
	weight = fields.Integer(string='Weight')
	start_date = fields.Date(string='Start Date')
	end_date = fields.Date(string='End Date')
	harga_satuan = fields.Integer(string='Harga Satuan')
	total_harga = fields.Integer(string='Total Harga')
	tax = fields.Float(string="Tax")

class monitoring_progress(models.Model):
	_name = 'monitoring.progress'

	contract_id = fields.Many2one('sale.order', string='Contract No', required=True)
	partner_id = fields.Many2one('sale.order', string='Customer Name', track_visibility='onchange')
	partner_invoice_id = fields.Many2one('sale.order', string='Customer Address', track_visibility='onchange')
	project_name_id = fields.Many2one('sale.order', string='Project Name', track_visibility='onchange')
	revenue_date = fields.Date(string='Revenue Date', required=True)
	currency_id = fields.Char(string='Currency')
	tp_aktual = fields.Char(string='Total Progress Aktual (%)')
	ap_aktual = fields.Char(string='Akumulasi Progress Aktual (%)')
	tp_approved = fields.Char(string='Total Progress Approved (%)')
	ap_approved = fields.Char(string='Akumulasi Progress Approved (%)')
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
	detail_line = fields.One2many('detail.invoice','detail_id')
	kwitansi_line = fields.One2many('kwitansi.invoice','kwitansi_id')
	faktur_line = fields.One2many('faktur.invoice','faktur_id')

	# @api.multi
 #    def cetak_faktur(self):
 #        return self.env['report'].get_action(self, 'sti_contract.laporan_faktur')
	
class detail_invoice(models.Model):
	_name = 'detail.invoice'

	detail_id = fields.Many2one('form.invoice','Detail')
	no_invoice = fields.Char(string='No.')
	work_description = fields.Char(string='Work Description')
	progress_date = fields.Date(string='Progress Date')
	progress_aktual = fields.Float(string='Progress Aktual')
	progress_approved = fields.Float(string='Progress Approved')
	tax = fields.Float(string='Tax')
	nilai_invoice = fields.Float(string='Nilai Invoice')

class kwitansi_invoice(models.Model):
	_name = 'kwitansi.invoice'

	kwitansi_id = fields.Many2one('form.invoice',string='Kwitansi')
	no_kwitansi = fields.Char(string='No. Kwitansi',readonly=True)
	tanggal_kwitansi = fields.Date(string='Tanggal Kwitansi')

class faktur_line(models.Model):
	_name = 'faktur.invoice'

	faktur_id = fields.Many2one('form.invoice',string='Faktur')
	no_faktur = fields.Char(string='No Faktur', readonly=True)
	tanggal_faktur = fields.Date(string='Tanggal Faktur')