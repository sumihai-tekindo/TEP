from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class SPB(models.Model):
	_name = 'spb'
	_inherit = ['mail.thread']

	name				= fields.Char(string="No SPB",default="New")
	tanggal_spb			= fields.Date(string="Date",default=fields.Date.today)
	proyek_id			= fields.Many2one('project.project',string="Project", required=True, track_visibility='always')
	departemen_id		= fields.Many2one('hr.department',string="Department")
	budgeted			= fields.Selection([('yes','Yes'),('no','No')],string="Budgeted")
	sifat_kebutuhan		= fields.Char(string="Sifat Kebutuhan")
	tanggal_diperlukan	= fields.Date(string="Tanggal Diperlukan",default=fields.Date.today)
	nomer_gambar 		= fields.Many2one('project.document',string="No Gambar") 
	notes				= fields.Text('Terms and Conditions')
	spb_line_ids		= fields.One2many('spb.line', 'spb_id')
	state				= fields.Selection([('draft', 'New'),
											('confirm', 'QS'),
											('approved', 'PM'),
											('done', 'Done'),
											('cancel', 'Cancel')],
											string="Status", default="draft", track_visibility='onchange')
	company_id			= fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	notes 				= fields.Text('Terms and Conditions')

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('spb.sequence') or '/'
			code = self.env['project.project'].browse(vals['proyek_id']).code
			if code:
				vals['name'] = vals['name'][:10]+'/TEP-'+code+vals['name'][10:]
		return super(SPB, self).create(vals)

	@api.multi
	def unlink(self):
		for spb in self:
			if not spb.state == 'cancel':
				raise UserError(_('You must cancel this SPB first before delete'))
		return super(SPB, self).unlink()
	
	@api.multi
	def button_sendtodraft(self):
		self.write({'state': 'draft'})

	@api.multi
	def button_confirm(self):
		self.write({'state': 'confirm'})

	@api.multi
	def button_submit2pm(self):
		self.write({'state': 'approved'})

	@api.multi
	def button_approve(self):
		self.write({'state': 'done'})

	@api.multi
	def button_done(self):
		self.write({'state': 'done'})

	@api.multi
	def button_cancel(self):
		self.write({'state': 'cancel'})

class SPBLine(models.Model):
	_name = 'spb.line'

	@api.multi
	@api.constrains('jumlah_permintaan')
	def _check_jumlah_permintaan(self):
		for record in self:
			if record.jumlah_permintaan <= 0.0:
				raise ValidationError(_('Cannot insert jumlah permintaan less than 0 or same with 0. (Product: %s)') % record.product_id.name)

	name 				= fields.Char(string="Description")
	product_id 			= fields.Many2one('product.product', required=True, string="Product")
	satuan 				= fields.Many2one('product.uom', string="Satuan")
	jumlah_permintaan 	= fields.Float(string="Jumlah Permintaan", required=True)
	account_analytic 	= fields.Many2one('account.analytic.account', string="Account Analytic") 
	quantity_transfer 	= fields.Float(string="Quantity Transfer", compute="compute_it")
	quantity_po 		= fields.Float(string="Quantity PO", compute="compute_po")
	outstanding_spb 	= fields.Float(string="Outstanding SPB", compute="sum_outstanding_spb")
	state 				= fields.Selection(related="spb_id.state", store=True, default="draft", string="Status")
	spb_id 				= fields.Many2one('spb')

	@api.onchange('product_id')
	def description_product(self):
		result = {}
		if not self.product_id:
			return result

		self.satuan = self.product_id.uom_po_id or self.product_id.uom_id
		result['domain'] = {'satuan': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
		product_lang = self.product_id.with_context(
			lang=self.env.user.lang
		)
		self.name = product_lang.display_name

		return result

	@api.multi
	def compute_it(self):
		for record in self:
			try:
				current_id = record.id or record._origin.id
			except:
				current_id=False
			if current_id:
				spb_lines = self.env['spb.line'].search([('product_id','=',record.product_id.id),('id','in',[y.id for y in record.spb_id.spb_line_ids])],order='id asc')
				qty_po =sum(record.get_qty_it(record.spb_id.id,record.product_id.id))
				for x in spb_lines:
					if x.id!=record.id:
						if qty_po>=x.jumlah_permintaan:
							qty_po=qty_po-x.jumlah_permintaan
						else:
							qty_po=0.0
					else:
						if qty_po<=record.jumlah_permintaan:
							record.quantity_transfer=qty_po	
						else:
							record.quantity_transfer=record.jumlah_permintaan
							qty_po=qty_po-record.jumlah_permintaan

	@api.multi
	def compute_po(self):
		for record in self:
			try:
				current_id = record.id or record._origin.id
			except:
				current_id=False
			if current_id:
				spb_lines = self.env['spb.line'].search([('product_id','=',record.product_id.id),('id','in',[y.id for y in record.spb_id.spb_line_ids])],order='id asc')
				qty_po =sum(record.get_qty_po(record.spb_id.id,record.product_id.id))
				for x in spb_lines:
					if x.id!=record.id:
						if qty_po>=x.jumlah_permintaan:
							qty_po=qty_po-x.jumlah_permintaan
						else:
							qty_po=0.0
					else:
						if qty_po<=record.jumlah_permintaan:
							record.quantity_po=qty_po	
						else:
							record.quantity_po=record.jumlah_permintaan
							qty_po=qty_po-record.jumlah_permintaan

	def get_qty_po(self,spb_id, product_id):
		result = []
		product_qtys = self.env['purchase.order.line'].search([('spb_id','=',spb_id),('product_id','=',product_id)])
		if product_qtys:
			result = [x.product_qty for x in product_qtys]
		return result 

	def get_qty_it(self,spb_id,product_id):
		result = []
		product_uom_qtys = self.env['stock.move'].search([('picking_id.spb_id','=',spb_id),('product_id','=',product_id)])
		if product_uom_qtys:
			return [y.product_uom_qty for y in product_uom_qtys]
		return result 

	@api.depends('jumlah_permintaan','quantity_transfer','quantity_po')
	def sum_outstanding_spb(self):
		for record in self:
			record.outstanding_spb = record.jumlah_permintaan-(record.quantity_transfer+record.quantity_po)

	@api.multi
	def view_po_for_spbline(self):
		self.ensure_one()
		po_ids = self.env['purchase.order.line'].search([('spb_id','=',self.spb_id.id),('product_id','=',self.product_id.id)])
		return {
			'type'		: 'ir.actions.act_window',
			'name'		: 'Purchase Orders',
			'view_type'	: 'form',
			'view_mode'	: 'tree,form',
			'domain' 	: str([('id','in',tuple([po.order_id.id for po in po_ids]))]),
			'res_model'	: 'purchase.order',
		}

	@api.multi
	def view_sjl_for_spbline(self):
		self.ensure_one()
		sjl_ids = self.env['stock.move'].search([('picking_id.spb_id','=',self.spb_id.id),('product_id','=',self.product_id.id)])
		return {
			'type'		: 'ir.actions.act_window',
			'name'		: 'Surat Jalan',
			'view_type'	: 'form',
			'view_mode'	: 'tree,form',
			'domain' 	: str([('id','in',tuple([picking.picking_id.id for picking in sjl_ids]))]),
			'res_model'	: 'stock.picking',
		}

class SPBWizard(models.TransientModel):
	_name = 'spb.wizard'

	pilihan_wizard 		= fields.Selection([('po','Purchase Order'),('it','Inventory Transfer')] ,default="po")
	buat_baru 			= fields.Selection([('yes','Yes'),('no','No')],string="Buat Baru",default="yes")
	purchase_id 		= fields.Many2one('purchase.order')
	internal_id 		= fields.Many2one('stock.picking',domain=[('state','=','draft'),('picking_type_code','=','internal'), ('type_bon','=',False)])
	partner_id 			= fields.Many2one('res.partner',string="Vendor")

	@api.onchange('buat_baru')
	def domain_purchase_id(self):
		spb_line = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))
		po_id = self.env['purchase.order'].search([('project_id','=',spb_line.spb_id.proyek_id.id)])
		return  {'domain':{'purchase_id':[('state','=','draft'),('id','in', ([x.id for x in po_id]))]}}

	@api.multi
	def btn_wizard(self):
		picking = self.env['stock.picking']
		model_aktif = self.env.context.get('active_model')
		id_aktif = self.env.context.get('active_id')
		transfer_picking_type = self.env.user.company_id.picking_type_id
		browse_spb_line = self.env[model_aktif].browse(id_aktif)
		
		if browse_spb_line.outstanding_spb>0:
			if (self.pilihan_wizard == 'po') and (self.buat_baru == 'yes'):
				if model_aktif == 'spb.line':
					data_spb = {
						'partner_id':self.partner_id.id,
						'project_id':browse_spb_line.spb_id.proyek_id.id,
						'origin':browse_spb_line.spb_id.name,
					}

					purchase_order	= self.env['purchase.order']
					new_po = purchase_order.new(data_spb)
					new_po._set_receipt()
					order = purchase_order.create(new_po._convert_to_write(new_po._cache))
					order_lines = self.env['purchase.order.line']

					data_po_line = {'product_id': browse_spb_line.product_id.id}

					line_cache = order_lines.new(data_po_line)
					line_cache.onchange_product_id()
				
					data_po_line.update(dict(line_cache._convert_to_write(line_cache._cache), 
						spb_id=browse_spb_line.spb_id.id, 
						product_qty=browse_spb_line.outstanding_spb,
						order_id= order.id,
						date_planned=browse_spb_line.spb_id.tanggal_diperlukan,))

					new_lines = order_lines.create(data_po_line)
					
					return {
						'type': 'ir.actions.act_window',
						'name': 'Purchase Orders',
						'view_type': 'form',
						'view_mode': 'tree,form',
						'domain' : str([('id', '=', order.id)]),
						'res_model': 'purchase.order',
					}
			
			elif (self.pilihan_wizard == 'po') and (self.buat_baru == 'no'):
				if model_aktif == 'spb.line':

					order_lines 	= self.env['purchase.order.line']
					data_po_line 	= {'product_id': browse_spb_line.product_id.id}
					line_cache 		= order_lines.new(data_po_line)
					origin			= self.purchase_id.origin+','+browse_spb_line.spb_id.name

					self.purchase_id.write({'origin': origin})

					line_cache.onchange_product_id()
					data_po_line.update(
						dict(line_cache._convert_to_write(line_cache._cache),
						spb_id=browse_spb_line.spb_id.id,
						product_qty=browse_spb_line.outstanding_spb,
						order_id= self.purchase_id.id,
						date_planned=browse_spb_line.spb_id.tanggal_diperlukan,)
					)

					new_lines 		= order_lines.create(data_po_line)
					
					po_ids = self.env['purchase.order.line'].search([('spb_id','=',browse_spb_line.spb_id.id),('product_id','=',browse_spb_line.product_id.id)])
					return {
						'type': 'ir.actions.act_window',
						'name': 'Purchase Orders',
						'view_type': 'form',
						'view_mode': 'tree,form',
						'domain' : str([('id','in',tuple([po.order_id.id for po in po_ids]))]),
						'res_model': 'purchase.order',
					}

			elif (self.pilihan_wizard == 'it') and (self.buat_baru == 'yes'):
				if model_aktif == 'spb.line':

					data_picking = {
							'spb_id'			: browse_spb_line.spb_id.id,
							'project_id'		: browse_spb_line.spb_id.proyek_id.id,
							'picking_type_id'	: transfer_picking_type.id,
							'location_id'		: transfer_picking_type.default_location_src_id.id,
							'location_dest_id'	: browse_spb_line.spb_id.proyek_id.location_id.id,
							'company' 			: self.env.user.company_id.id,
							'move_type' 		: 'direct',
						}

					stock_picking = self.env['stock.picking'].create(data_picking)
					
					data_stock_move = {
							'date_expected'		: fields.Date.context_today(self), #ini sesuai tanggal diperlukan spb cek juga d stock picking?
							'product_id'		: browse_spb_line.product_id.id,
							'product_uom'		: browse_spb_line.product_id.uom_id.id,
							'picking_id'		: stock_picking.id,
							'product_uom_qty'	: browse_spb_line.outstanding_spb,
							'state'				: 'draft',
							'location_dest_id'	: browse_spb_line.spb_id.proyek_id.location_id.id,
							'location_id'		: transfer_picking_type.default_location_src_id.id,
							'name'				: browse_spb_line.product_id.name,
						}

					stock_move = self.env['stock.move'].create(data_stock_move)

					return {
						'type'		: 'ir.actions.act_window',
						'name'		: 'Surat Jalan',
						'view_type'	: 'form',
						'view_mode'	: 'tree,form',
						'domain' 	: str([('id', '=', stock_picking.id)]),
						'res_model'	: 'stock.picking',
						'context'	: {
							'search_default_picking_type_id': [transfer_picking_type.id],
							'default_picking_type_id': transfer_picking_type.id,
							'contact_display': 'partner_address',
						}
					}

			elif (self.pilihan_wizard == 'it') and (self.buat_baru == 'no'):
				if model_aktif == 'spb.line':

					data_stock_move = {
							'picking_id'		: self.internal_id.id,
							'date_expected'		: fields.Date.context_today(self), #ini sesuai tanggal diperlukan spb cek juga d stock picking?
							'product_id'		: browse_spb_line.product_id.id,
							'product_uom'		: browse_spb_line.product_id.uom_id.id,
							'product_uom_qty'	: browse_spb_line.outstanding_spb,
							'state'				: 'draft',
							'location_dest_id'	: browse_spb_line.spb_id.proyek_id.location_id.id,
							'location_id'		: transfer_picking_type.default_location_src_id.id,
							'name'				: browse_spb_line.product_id.name,
						}

					stock_move = self.env['stock.move'].create(data_stock_move)

					it_ids = self.env['stock.move'].search([('spb_id','=',browse_spb_line.spb_id.id),('product_id','=',browse_spb_line.product_id.id)])
					return {
						'type': 'ir.actions.act_window',
						'name': 'Surat Jalan',
						'view_type': 'form',
						'view_mode': 'tree,form',
						'domain' : str([('id','in',tuple([x.picking_id.id for x in it_ids]))]),
						'res_model': 'stock.picking',
						'context': {
							'search_default_picking_type_id': [transfer_picking_type.id],
							'default_picking_type_id': transfer_picking_type.id,
							'contact_display': 'partner_address',
						}
					}
		else:
			raise ValidationError(_("Unable to create Purchase Order, you have no outstanding qty for this product"))

class Company(models.Model):

	_inherit = 'res.company'

	picking_type_id = fields.Many2one('stock.picking.type', string="Type Inventory Transfer SPB")