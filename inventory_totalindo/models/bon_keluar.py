from odoo import models,fields,api
	
class OperationTypes(models.Model):

	_inherit = 'stock.picking.type'

	type_bon = fields.Selection([('in','Bon Material Masuk'),('out','Bon Material Keluar')],string="Create as",default=False)