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
		# TDE FIXME: clean that brol
		defaults = self.default_get(['name', 'picking_type_id'])
		if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
			vals['name'] = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
			code = self.env['project.project'].browse(vals['project_id']).code
			vals['name'] = vals['name'][:10]+'/TEP-'+code+vals['name'][10:]
			
		# TDE FIXME: what ?
		# As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
		# As it is a create the format will be a list of (0, 0, dict)
		if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
			for move in vals['move_lines']:
				if len(move) == 3:
					move[2]['location_id'] = vals['location_id']
					move[2]['location_dest_id'] = vals['location_dest_id']
		return super(StockPicking, self).create(vals)
		
		
class StockPickingOperation(models.Model):

	_inherit = 'stock.pack.operation'

	deskripsi = fields.Text(string="Deskripsi/Merk")
	keterangan = fields.Text(string="Keterangan")
	kondisi = fields.Text(string="Kondisi")