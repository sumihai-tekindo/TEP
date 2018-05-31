from odoo import models,fields,api
import json
	
class StockPicking(models.Model):

	_inherit = 'stock.picking'

	project_id 		= fields.Many2one('project.project', string="Project", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, required=True)
	type_spm 		= fields.Selection([('by_po','By Purchase Order'),
										('by_cash','By Cash'),
										('by_transfer', 'By Transfer'),
										('by owner','By Owner')],
										string="Type", default=False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
	no_polisi 		= fields.Char(string="Diangkut Dengan", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
	spb_id 			= fields.Many2one('spb', string="No SPB")
	penerima 		= fields.Char(string="Penerima")
	user 			= fields.Many2one('res.users', string="User", readonly=True)
	department 		= fields.Many2one('hr.department', string="Department")
	peminjam 		= fields.Char(string="Peminjam")
	no_sjl			= fields.Many2one('stock.picking', string="No Surat Jalan", domain=[('name','ilike','SJL'),('state','=','done')])
	type_bon 		= fields.Selection(related='picking_type_id.type_bon',store=True, default=False)
	# type_bok 	= fields.Selection([('dipakai','Dipinjam'),('dipinjam','Dipakai')], default=False, string="Type")
	

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
		
		print json.dumps(vals, indent=2)	
		return super(StockPicking, self).create(vals)
		
	@api.onchange('spb_id','no_sjl')
	def change_stock_move(self):
		move_lines=[]

		if self.spb_id:
			self.project_id = self.spb_id.proyek_id.id
			self.location_dest_id = self.spb_id.proyek_id.location_id.id or self.location_dest_id or False
			
			self.with_context({
					'default_location_id'		:self.location_id.id,
					'default_location_dest_id'	:self.location_dest_id.id,
				})

			for spb_line in self.spb_id.spb_line_ids:
				data = {
					'date_expected'		: fields.Date.context_today(self), #ini sesuai tanggal diperlukan spb?
					'product_id'		: spb_line.product_id.id,
					'product_uom'		: spb_line.product_id.uom_id.id,
					'picking_type_id'	: self.picking_type_id.id,
					'product_uom_qty'	: spb_line.outstanding_spb,
					'state'				: 'draft',
					'location_dest_id'	: self.location_dest_id.id,
					'location_id'		: self.location_id.id,
					'name'				: spb_line.product_id.name,
				}
				move_lines.append(data)
		
		elif self.no_sjl:
			self.location_id = self.no_sjl.location_dest_id.id
			self.location_dest_id = self.no_sjl.location_id.id

			self.with_context({
					'default_location_id'		:self.location_id.id,
					'default_location_dest_id'	:self.location_dest_id.id,
				})

			for line in self.no_sjl.move_lines:
				data = {
					'date_expected'		: line.date_expected,
					'product_id'		: line.product_id.id,
					'product_uom'		: line.product_uom.id,
					'picking_type_id'	: self.picking_type_id.id,
					'product_uom_qty'	: line.product_uom_qty,
					'state'				: 'draft',
					'location_dest_id'	: self.location_dest_id.id,
					'location_id'		: self.location_id.id,
					'name'				: line.name,
				}
				move_lines.append(data)
		self.move_lines = move_lines

		if self.type_bon == 'out':
			self.user = self.spb_id.create_uid.id
			self.department = self.spb_id.departemen_id.id

	
	