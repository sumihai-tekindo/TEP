from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
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
	budegeted			= fields.Selection([('yes','Yes'),('no','No')],string="Budgeted")
	sifat_kebutuhan		= fields.Char(string="Sifat Kebutuhan")
	tanggal_diperlukan	= fields.Date(string="Tanggal Diperlukan",default=fields.Date.today)
	nomer_gambar 		= fields.Many2one('project.document',string="No Gambar") 
	notes				= fields.Text('Terms and Conditions')
	spb_line_ids		= fields.One2many('spb.line', 'spb_id')
	state				= fields.Selection([
		('draft', 'New'),
		('confirm', 'QS'),
		('approved', 'PM'),
		('done', 'Done'),
		('cancel', 'Cancel')],  
		string="Status",
		default="draft",
		track_visibility='onchange')

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

	name 				= fields.Char(string="Description")
	product_id 			= fields.Many2one('product.product', required=True, string="Product")
	satuan 				= fields.Many2one('product.uom', string="Satuan")
	jumlah_permintaan 	= fields.Float(string="Jumlah Permintaan", required=True)
	account_analytic 	= fields.Many2one('account.analytic.account', string="Account Analytic") 
	quantity_transfer 	= fields.Float(string="Quantity Transfer")
	quantity_po 		= fields.Float(string="Quantity PO", compute="compute_po")
	outstanding_spb 	= fields.Float(string="Outstanding SPB",store=True, compute="sum_outstanding_spb")
	state 				= fields.Selection(related="spb_id.state", store=True, default="draft", string="Status")
	spb_id 				= fields.Many2one('spb')
	po_lines			= fields.Many2many('purchase.order.line','spb_line_po_line_rel','spb_line_id','po_line_id')
	sjl_lines			= fields.Many2many('stock.move','spb_line_sjl_line_rel','spb_line_id','sjl_line_id')
	po_ids				= fields.Many2many('purchase.order', compute="set_po_ids")
	sjl_ids				= fields.Many2many('stock.picking', compute="set_sjl_ids")

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

	@api.depends('po_lines')
	def compute_po(self):
		for line in self:
			line.quantity_po = sum(po_lines.product_qty)

	# @api.multi
	# def compute_it(self):
	# 	for record in self:
	# 		record.quantity_transfer=sum(record.get_qty_it(record.spb_id.id,record.product_id.id))

	# @api.multi
	# def compute_po(self):
	# 	for record in self:
	# 		record.quantity_po=sum(record.get_qty_po(record.spb_id.id,record.product_id.id))

	# def get_qty_po(self,spb_id, product_id):
	# 	product_qtys = []
	# 	product_qtys = self.env['purchase.order.line'].search([('spb_id','=',spb_id),('product_id','=',product_id)])
	# 	return [x.product_qty for x in product_qtys] 

	# def get_qty_it(self,spb_id,product_id):
	# 	product_uom_qtys = []
	# 	product_uom_qtys = self.env['stock.move'].search([('picking_id.spb_id','=',spb_id),('product_id','=',product_id)])
	# 	return [y.product_uom_qty for y in product_uom_qtys] 

	@api.depends('jumlah_permintaan','quantity_transfer','quantity_po')
	def sum_outstanding_spb(self):
		for record in self:
			record.outstanding_spb = record.jumlah_permintaan-(record.quantity_transfer+record.quantity_po)

	@api.depends('po_lines.order_id')
	def set_po_ids(self):
		for record in self:
			record.po_ids=[x.order_id.id for x in record.po_lines]

	@api.depends('sjl_lines.picking_id')
	def set_sjl_ids(self):
		for record in self:
			record.sjl_ids=[x.picking_id.id for x in record.sjl_lines]

	@api.multi
	def view_po_for_spbline(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Purchase Orders',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'domain' : str([('id','in',tuple([po.id for po in self.po_ids]))]),
			'res_model': 'purchase.order',
		}

	@api.multi
	def view_sjl_for_spbline(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Surat Jalan',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'domain' : str([('id','in',tuple([po.id for po in self.sjl_ids]))]),
			'res_model': 'stock.picking',
		}

class SPBWizard(models.TransientModel):
	_name = 'spb.wizard'

	pilihan_wizard 		= fields.Selection([('po','Purchase Order'),('it','Inventory Transfer')] ,default="po")
	buat_baru 			= fields.Selection([('yes','Yes'),('no','No')],string="Buat Baru",default="yes")
	purchase_id 		= fields.Many2one('purchase.order',domain=[('state','=','draft')])
	internal_id 		= fields.Many2one('stock.picking',domain=[('state','=','draft'),('picking_type_code','=','internal'), ('type_bon','=',False)])
	partner_id 			= fields.Many2one('res.partner',string="Vendor")

	@api.multi
	def btn_wizard(self):
		picking = self.env['stock.picking']
		model_aktif = self.env.context.get('active_model')
		id_aktif = self.env.context.get('active_id')
		transfer_picking_type = self.env.user.company_id.picking_type_id

		if (self.pilihan_wizard == 'po') and (self.buat_baru == 'yes'):
			if model_aktif == 'spb.line':
				browse_spb_line = self.env[model_aktif].browse(id_aktif)

				data_spb = {
					'partner_id':self.partner_id.id,
					'project_id':browse_spb_line.spb_id.proyek_id.id,
					'origin':browse_spb_line.spb_id.name,
				}

				order		= self.env['purchase.order'].create(data_spb)
				order_lines = self.env['purchase.order.line']

				data_po_line = {
					'product_id': browse_spb_line.product_id.id,
				}

				line_cache = order_lines.new(data_po_line)
				line_cache.onchange_product_id()
			
				data_po_line.update(dict(line_cache._convert_to_write(line_cache._cache), 
					spb_id=browse_spb_line.spb_id.id, 
					product_qty=browse_spb_line.outstanding_spb,
					order_id= order.id,
					date_planned=browse_spb_line.spb_id.tanggal_diperlukan,))

				new_lines = order_lines.create(data_po_line)
				self.env.cr.execute('insert into spb_line_po_line_rel (spb_line_id,po_line_id) values (%d,%d)'%(browse_spb_line.id,new_lines.id))
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

				browse_spb_line = self.env[model_aktif].browse(id_aktif)
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
				
				self.env.cr.execute('insert into spb_line_po_line_rel (spb_line_id,po_line_id) values (%d,%d)'%(browse_spb_line.id,new_lines.id))

				return {
					'type': 'ir.actions.act_window',
					'name': 'Purchase Orders',
					'view_type': 'form',
					'view_mode': 'tree,form',
					'domain' : str([('id', '=', self.purchase_id.id)]),
					'res_model': 'purchase.order',
				}

		elif (self.pilihan_wizard == 'it') and (self.buat_baru == 'yes'):
			if model_aktif == 'spb.line':
				browse_spb_line = self.env[model_aktif].browse(id_aktif)

				data_picking = {
					'spb_id':browse_spb_line.spb_id.id,
					'project_id':browse_spb_line.spb_id.proyek_id.id,
					'picking_type_id':transfer_picking_type.id,
					'location_id': transfer_picking_type.default_location_src_id.id,
					'location_dest_id': transfer_picking_type.default_location_dest_id.id,
					'company' : self.env.user.company_id.id,
					'move_type' : 'direct',
				}

				stock_picking = self.env['stock.picking'].create(data_picking)
				stock_move = self.env['stock.move']

				data_stock_move = {
					'product_id': browse_spb_line.product_id.id
				}

				line_cache = stock_move.new(data_stock_move)
				line_cache.onchange_product_id()
			
				data_stock_move.update(dict(line_cache._convert_to_write(line_cache._cache), 
						picking_id = stock_picking.id,
						name = browse_spb_line.product_id.partner_ref,
						product_uom = browse_spb_line.product_id.uom_id.id,
						product_uom_qty = browse_spb_line.outstanding_spb,
						state = 'draft',
						location_id = transfer_picking_type.default_location_src_id.id,
						location_dest_id = transfer_picking_type.default_location_dest_id.id,
						company_id = self.env.user.company_id.id,
						procure_method = 'make_to_stock',
						date = fields.Date.context_today(self),
						date_expected = fields.Date.context_today(self),
					))

				stock_move = stock_move.create(data_stock_move)
				self.env.cr.execute('insert into spb_line_sjl_line_rel (spb_line_id,sjl_line_id) values (%d,%d)'%(browse_spb_line.id,stock_move.id))
				return {
					'type': 'ir.actions.act_window',
					'name': 'Surat Jalan',
					'view_type': 'form',
					'view_mode': 'tree,form',
					'domain' : str([('id', '=', stock_picking.id)]),
					'res_model': 'stock.picking',
					'context': {
						'search_default_picking_type_id': [transfer_picking_type.id],
						'default_picking_type_id': transfer_picking_type.id,
						'contact_display': 'partner_address',
					}
				}

		elif (self.pilihan_wizard == 'it') and (self.buat_baru == 'no'):
			if model_aktif == 'spb.line':
				browse_spb_line = self.env[model_aktif].browse(id_aktif)

				stock_move = self.env['stock.move']

				data_stock_move = {
					'product_id': browse_spb_line.product_id.id
				}

				line_cache = stock_move.new(data_stock_move)
				line_cache.onchange_product_id()
			
				data_stock_move.update(dict(line_cache._convert_to_write(line_cache._cache), 
						picking_id = self.internal_id.id,
						name = browse_spb_line.product_id.partner_ref,
						product_uom = browse_spb_line.product_id.uom_id.id,
						product_uom_qty = browse_spb_line.outstanding_spb,
						state = 'draft',
						location_id = transfer_picking_type.default_location_src_id.id,
						location_dest_id = transfer_picking_type.default_location_dest_id.id,
						company_id = self.env.user.company_id.id,
						procure_method = 'make_to_stock',
						date = fields.Date.context_today(self),
						date_expected = fields.Date.context_today(self),
					))

				stock_move = stock_move.create(data_stock_move)
				self.env.cr.execute('insert into spb_line_sjl_line_rel (spb_line_id,sjl_line_id) values (%d,%d)'%(browse_spb_line.id,stock_move.id))
				return {
					'type': 'ir.actions.act_window',
					'name': 'Surat Jalan',
					'view_type': 'form',
					'view_mode': 'tree,form',
					'domain' : str([('id', '=', self.internal_id.id)]),
					'res_model': 'stock.picking',
					'context': {
						'search_default_picking_type_id': [transfer_picking_type.id],
						'default_picking_type_id': transfer_picking_type.id,
						'contact_display': 'partner_address',
					}
				}

class Company(models.Model):

	_inherit = 'res.company'

	picking_type_id = fields.Many2one('stock.picking.type', string="Type Inventory Transfer SPB")