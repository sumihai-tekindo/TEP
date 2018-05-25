from odoo import models,fields,api
	
class StockPicking(models.Model):

	_inherit = 'stock.picking'

	project_id 	= fields.Many2one('project.project', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, required=True)
	department 	= fields.Many2one('hr.department', string="Department")
	spb_id 		= fields.Many2one('spb', string="No SPB")
	no_polisi 	= fields.Char(string="Diangkut Dengan", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
	penerima 	= fields.Char(string="Penerima")
	user 		= fields.Char(string="User")
	type_bon 	= fields.Selection(related='picking_type_id.type_bon',store=True, default=False)
	type_bok 	= fields.Selection([('dipakai','Dipinjam'),('dipinjam','Dipakai')], default=False, string="Type")
	type_spm 	= fields.Selection([
		('by_PO','by purchase order'),
		('by_cash','by cash'),
		('by_transfer', 'by transfer'),
		('by owner','by owner')],
		string="Type", 
		default=False,
		states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

	@api.model
	def create(self, vals):
		defaults = self.default_get(['name', 'picking_type_id'])
		if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
			vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
			code = self.env['project.project'].browse(vals['project_id']).code
			if code:
				vals['name'] = vals['name'][:10]+'/TEP-'+code+vals['name'][10:]
			
		if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
			for move in vals['move_lines']:
				if len(move) == 3:
					move[2]['location_id'] = vals['location_id']
					move[2]['location_dest_id'] = vals['location_dest_id']
		return super(StockPicking, self).create(vals)
		
	@api.onchange('spb_id')
	def change_stock_move(self):
		self.project_id = self.spb_id.proyek_id.id
		self.location_dest_id = self.spb_id.proyek_id.location_id.id
		move_lines=[]
		data = []
		if self.spb_id:
			for spb_line in self.spb_id.spb_line_ids:
				data = {
					'product_id': spb_line.product_id.id,
					# 'name' : spb_line.product_id.partner_ref,
        			# 'product_uom': spb_line.product_id.uom_id.id,
					'product_uom_qty': spb_line.outstanding_spb,
					'state': 'draft',
					# 'location_id': self.location_id.id,
					# 'location_dest_id' : self.location_dest_id.id,
					# 'company_id' : self.env.user.company_id.id,
					# 'procure_method':'make_to_stock',
					# 'date': fields.Date.context_today(self),
					# 'date_expected': fields.Date.context_today(self),
				}
				move_lines.append(data)
		
		self.move_lines = move_lines

class StockPickingOperation(models.Model):

	_inherit = 'stock.pack.operation'

	deskripsi = fields.Text(string="Deskripsi/Merk")
	keterangan = fields.Text(string="Keterangan")
	kondisi = fields.Text(string="Kondisi")