from odoo import models,fields,api
	
class InventoryAdjustments(models.Model):

	_inherit = 'stock.inventory'

	name_code = fields.Char(default="New")
	type_barang = fields.Selection([('diubah_bentuk','Diubah bentuk'),('hilang','Hilang'),('rusak', 'Rusak'),('dihibahkan','Dihibahkan'),('dijual','Dijual')],string="Type", default=False)
	oleh = fields.Char(string="Oleh")
	department_id = fields.Many2one('hr.department', string="Department")
	referensi = fields.Char(string="Referensi", required=True)
	
	@api.model
	def create(self, vals):
		if vals.get('name_code', 'New') == 'New':
			vals['name_code'] = self.env['ir.sequence'].next_by_code('adj.sequence.inherit') or '/'
		return super(InventoryAdjustments, self).create(vals)