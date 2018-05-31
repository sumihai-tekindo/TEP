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
	task_id = fields.Many2one('project.task', 'Project Task')
	sale_charge_id = fields.Many2one('sale.charge.config', 'Sale Charge Config', readonly=True, required=True,
									 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	project_code = fields.Char(string='Project Code', readonly=True)
	start_date = fields.Date(string='Start Date', required=True)
	end_date = fields.Date(string='End Date', required=True)
	payment_term = fields.Selection([('15 hari', '15 Hari'), ('akhir bulan', 'Akhir Bulan')], string='Payment Term')
	nilai_dp = fields.Float(string='Nilai Down Payment')
	nilai_retensi = fields.Float(string='Nilai Retensi')
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

	@api.onchange('contract_no','amandement')
	def onchange_amandement(self):
		self.partner_id = self.contract_no.partner_id.id
		self.start_date = self.contract_no.start_date
		self.end_date = self.contract_no.end_date
		self.contract_id = self.contract_no.contract_id.id
		self.nilai_dp = self.contract_no.nilai_dp
		self.nilai_retensi = self.contract_no.nilai_retensi
		if not self.contract_no or not self.amandement or self.amandement=='tambah':
			self.order_line=False
		else:
			order_line=[]
			l={}
			for line in self.contract_no.order_line:
				l.update({
					'name':line.name,
					'product_id':line.product_id.id,
					'no_task':line.no_task,
					'product_uom_qty':line.product_uom_qty,
					'product_uom':line.product_uom.id,
					'price_unit':line.price_unit,
					'uraian':line.uraian,
					'tax_id':line.tax_id,
					'keterangan':line.keterangan,
					})
				order_line.append(l)
			self.order_line=order_line

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
