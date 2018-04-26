from odoo import models,fields,api
	
class SpmHeader(models.Model):

	_inherit = 'stock.picking'

	project_id = fields.Many2one('project.project' ,string="Nama Project")
	type_spm = fields.Selection([('by_PO','by PO'),('by_cash','by cash'),('by_transfer', 'by transfer'),('by owner','by owner')],string="Type", default=False)
	no_polisi = fields.Char(string="Diangkut dengan")

class SpmLine(models.Model):

	_inherit = 'stock.pack.operation'

	deskripsi = fields.Text(string="Deskripsi/Merk")
	keterangan = fields.Text(string="Keterangan")
	kondisi = fields.Text(string="Kondisi")

	@api.onchange('deskripsi')
	def tes(self):
		print(self.picking_id.picking_type_code)