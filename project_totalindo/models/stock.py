from odoo import api, fields, models, _

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"
    
    project_id = fields.Many2one('project.project', string='Project')
    
