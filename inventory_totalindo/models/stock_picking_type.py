from odoo import models,fields,api
	
class StockPickingType(models.Model):

	_inherit = 'stock.picking.type'

	type_bon = fields.Selection([('in','Bon Masuk'),('out','Bon Keluar')], string="Create as", default=False)