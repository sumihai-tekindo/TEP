from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
import odoo.addons.decimal_precision as dp

class SPB(models.Model):
	_name = 'spb'

	name				= fields.Char(string="Nomer SPB",default="New")
	tanggal_spb			= fields.Date(string="Tanggal SPB",default=fields.Date.today)
	proyek_id			= fields.Many2one('project.project',string="Proyek", required=True)
	departemen_id		= fields.Many2one('hr.department',string="Departemen")
	budegeted			= fields.Selection([('yes','Yes'),('no','No')],string="Budgeted")
	sifat_kebutuhan		= fields.Char(string="Sifat Kebutuhan")
	tanggal_diperlukan	= fields.Date(string="Tanggal Diperlukan",default=fields.Date.today)
	nomer_gambar 		= fields.Many2one('project.document',string="Nomer Gambar") 
	notes				= fields.Text('Terms and Conditions')
	spb_line_ids		= fields.One2many('spb.line', 'spb_id')
	state				= fields.Selection([
		('draft', 'New'),
		('confirm', 'QS'),
		('approved', 'PM'),
		('done', 'Done'),
		('cancel', 'Cancel')],  
		string="Status",
		default="draft")

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('spb.sequence') or '/'
			code = self.env['project.project'].browse(vals['proyek_id']).code
			vals['name'] = vals['name'][:10]+'/TEP-'+code+vals['name'][10:]
		return super(SPB, self).create(vals)

	@api.multi
	def unlink(self):
		for order in self:
			if order.state in ('done'):
				raise UserError('You cannot delete a approved SPB.')
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
	quantity_transfer 	= fields.Float(readonly=True, string="Quantity Transfer")
	quantity_po 		= fields.Float(readonly=True, string="Quantity PO", compute="compute_po")
	outstanding_spb 	= fields.Float(readonly=True, string="Outstanding SPB", compute="sum_outstanding_spb")
	state 				= fields.Selection(related="spb_id.state", store=True, default="draft", string="Status")
	spb_id 				= fields.Many2one('spb')
	po_lines			= fields.Many2many('purchase.order.line','spb_line_po_line_rel','spb_line_id','po_line_id')
	po_ids				= fields.Many2many('purchase.order', compute="set_po_ids")

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
	def compute_po(self):
		for record in self:
			record.quantity_po=sum(po_line_rel.product_qty for po_line_rel in record.po_lines)
			
	@api.depends('jumlah_permintaan','quantity_transfer','quantity_po')
	def sum_outstanding_spb(self):
		for record in self:
			record.outstanding_spb = record.jumlah_permintaan-(record.quantity_transfer+record.quantity_po)

	@api.depends('po_lines.order_id')
	def set_po_ids(self):
		for record in self:
			record.po_ids=[x.order_id.id for x in record.po_lines]

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


class SPBWizard(models.TransientModel):
	_name = 'spb.wizard'

	pilihan_wizard 	= fields.Selection([('po','Purchase Order'),('it','Inventory Transfer')] ,default="po")
	buat_baru 		= fields.Selection([('yes','Yes'),('no','No')],string="Buat Baru",default="yes")
	purchase_id 	= fields.Many2one('purchase.order',domain=[('state','=','draft')])
	internal_id 	= fields.Many2one('stock.picking',domain=[('state','=','draft'),('picking_type_code','=','internal')])
	partner_id 		= fields.Many2one('res.partner',string="Vendor")
	proyek_id		= fields.Many2one('project.project',string="Proyek")

	@api.multi
	def btn_wizard(self):
		model_aktif = self.env.context.get('active_model')
		id_aktif = self.env.context.get('active_id')

		if (self.pilihan_wizard == 'po') and (self.buat_baru == 'yes'):
			if model_aktif == 'spb.line':
				browse_spb_line = self.env[model_aktif].browse(id_aktif)

				data_spb = {
					'partner_id':self.partner_id.id,
					'project_id':self.proyek_id.id,
					# 'date_order':fields.Datetime.now(),
					# 'date_planned':fields.Datetime.now(),
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

		# elif (self.pilihan_wizard == 'it') and (self.buat_baru == 'yes'):
		# 	if model_aktif == 'spb.line':
		# 		browse_spb_line = self.env[model_aktif].browse(id_aktif)

		# 		@api.model
		# 		def _prepare_picking(self):
		# 			if not self.group_id:
		# 				self.group_id = self.group_id.create({
		# 					'name': self.name,
		# 					'partner_id': self.partner_id.id
		# 				})
		# 			if not self.partner_id.property_stock_supplier.id:
		# 				raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
		# 			return {
		# 				'picking_type_id': self.picking_type_id.id,
		# 				'partner_id': self.partner_id.id,
		# 				'date': self.date_order,
		# 				'origin': self.name,
		# 				'location_dest_id': self._get_destination_location(),
		# 				'location_id': self.partner_id.property_stock_supplier.id,
		# 				'company_id': self.company_id.id,
		# 				'project_id': self.project_id.id,
		# 			}

		# 		order_lines = self.env['stock.move']

		# 		data_po_line = {
		# 			'product_id': browse_spb_line.product_id.id,
		# 		}

		# 		line_cache = order_lines.new(data_po_line)
		# 		line_cache.onchange_product_id()
			
		# 		data_po_line.update(dict(line_cache._convert_to_write(line_cache._cache), 
		# 			spb_id=browse_spb_line.spb_id.id, 
		# 			product_qty=browse_spb_line.outstanding_spb,
		# 			picking_id= ))

		# 		new_lines = order_lines.create(data_po_line)
		# 		self.env.cr.execute('insert into spb_line_po_line_rel (spb_line_id,po_line_id) values (%d,%d)'%(browse_spb_line.id,new_lines.id))
				
		# 		return {
		# 			'type': 'ir.actions.act_window',
		# 			'name': 'Purchase Orders',
		# 			'view_type': 'form',
		# 			'view_mode': 'tree,form',
		# 			'domain' : str([('id', '=', order.id)]),
		# 			'res_model': 'purchase.order',
		# 		}