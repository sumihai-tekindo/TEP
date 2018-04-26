from odoo import models,fields,api
	
class PurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	project_id = fields.Many2one('project.project', string = "Project")
	task_id = fields.Many2one('project.task', string = "Task", domain = "[('project_id','=',project_id)]")
	department_id = fields.Many2one('hr.department', string = "Department")
	contact_person = fields.Char(string = "Contact Person")

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('po.sequence.inherit') or '/'
		return super(PurchaseOrder, self).create(vals)

class PurchaseOrderLine(models.Model):

	_inherit = 'purchase.order.line'

	# spb_id = fields.Many2one('spb', string = "No SPB")

