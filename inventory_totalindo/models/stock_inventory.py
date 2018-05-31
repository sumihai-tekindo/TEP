from odoo import models,fields,api
	
class StockInventory(models.Model):

	_inherit = 'stock.inventory'

	name_code 		= fields.Char(default="New")
	type_barang 	= fields.Selection([('diubah_bentuk','Diubah bentuk'),
										('hilang','Hilang'),('rusak', 'Rusak'),
										('dihibahkan','Dihibahkan'),
										('dijual','Dijual')],string="Type", default=False)
	oleh 			= fields.Char(string="Oleh")
	department_id 	= fields.Many2one('hr.department', string="Department")
	referensi 		= fields.Char(string="Referensi", required=True)
	project_id 		= fields.Many2one('project.project', string="Project", required=True)
	# state = fields.Selection(selection_add=[('approved_pm','PM')])
	
	@api.model
	def create(self, vals):
		if vals.get('name_code', 'New') == 'New':
			vals['name_code'] = self.env['ir.sequence'].next_by_code('adj.sequence.inherit') or '/'
			code = self.env['project.project'].browse(vals['project_id']).code
			if code:
				vals['name_code'] = vals['name_code'][:10]+'/TEP-'+code+vals['name_code'][10:]
		return super(StockInventory, self).create(vals)