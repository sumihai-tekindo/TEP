from odoo import models,fields,api
	
class SPM(models.Model):

	_inherit = 'stock.picking'

	project_id = fields.Many2one('project.project',
								string="Nama Project",
								states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
	type_spm = fields.Selection([('by_PO','by purchase order'),('by_cash','by cash'),('by_transfer', 'by transfer'),('by owner','by owner')],
								string="Type", 
								default=False,
								states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
	no_polisi = fields.Char(string="Diangkut Dengan",
							states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('spm.sequence.inherit') or '/'
		return super(SPM, self).create(vals)

class SPMLine(models.Model):

	_inherit = 'stock.pack.operation'

	deskripsi = fields.Text(string="Deskripsi/Merk")
	keterangan = fields.Text(string="Keterangan")
	kondisi = fields.Text(string="Kondisi")