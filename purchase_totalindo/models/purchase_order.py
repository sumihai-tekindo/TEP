from odoo import models,fields,api
	
class PurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	project_id = fields.Many2one('project.project', string = "Project")
	task_id = fields.Many2one('project.task', string = "Task", domain = "[('project_id','=',project_id)]")
	department_id = fields.Many2one('hr.department', string = "Department")
	contact_person = fields.Char(string = "Contact Person")
	# work_progress = fields.Float(related = "task_id.progress", string = "Work Progress", store=True, readonly=True)
	# task_stage_id = fields.Many2one(related = "task_id.stage_id", string = "Phase", store=True, readonly=True)
