from odoo import models, fields, api

class product_template(models.Model):
    _inherit = 'product.template'

    is_freight_charge = fields.Boolean('Is Freight Charge')
    is_other_charge = fields.Boolean('Is Other Charge')
