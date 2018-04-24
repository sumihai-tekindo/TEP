from odoo import models, fields, api

class project_contract(models.Model):
	_inherit = 'project.project'

	# project_line = fields.One2many('sale.order','project_id')
	