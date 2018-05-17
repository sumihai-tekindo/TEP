from odoo import models,fields,api
	
class ResCompany(models.Model):

	_inherit = 'res.company'

	po_double_validation = fields.Selection(selection_add=[('three_step', 'Get 3 levels of approvals to confirm a purchase order')])
	po_double_validation_amount = fields.Monetary(default=5000000)
	po_third_validation_amount = fields.Monetary(string='Third validation amount', default=2000000000,
		help="Minimum amount for which a double validation is required")

class PurchaseConfigSettings(models.TransientModel):
	
	_inherit = 'purchase.config.settings'

	po_third_validation_amount = fields.Monetary(related='company_id.po_third_validation_amount', 
		string="Third validation amount *", currency_field='company_currency_id')

