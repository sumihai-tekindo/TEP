from odoo import models,fields,api
	
class InventoryAdjustments(models.Model):

	_inherit = 'stock.inventory'

	type_barang = fields.Selection([('diubah_bentuk','Diubah bentuk'),('hilang','Hilang'),('rusak', 'Rusak'),('dihibahkan','Dihibahkan'),('dijual','Dijual')],string="Type", default=False)
	oleh = fields.Char(string="Oleh")
	department_id = fields.Many2one('hr.department', string="Department")
	referensi = fields.Char(string="Referensi", required=True)
	peminjam = fields.Char(string="Peminjam")
	