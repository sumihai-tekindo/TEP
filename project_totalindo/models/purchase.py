from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    project_id = fields.Many2one('project.project', string='Project')
    
