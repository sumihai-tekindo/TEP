from odoo import models,fields,api

class StockPickingOperation(models.Model):

	_inherit = 'stock.pack.operation'

	deskripsi 	= fields.Text(string="Deskripsi/Merk")
	keterangan 	= fields.Text(string="Keterangan")
	kondisi 	= fields.Text(string="Kondisi")