from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    @api.depends('unit_planned', 'progress_ids.progress_unit')
    def _compute_progress(self):
        for task in self:
            task.progress_actual = sum([progress.progress_unit for progress in task.progress_ids]) / task.unit_planned if task.unit_planned > 0.0 else 0.0
    
    code = fields.Char(string='Code')
    day_planned = fields.Float(string='Planned Days')
    unit_planned = fields.Float(string='Target Units')
    uom_id = fields.Many2one('product.uom', string='UoM')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='UoM')
    amount = fields.Monetary(string='RAB Value')
    weight = fields.Float(string='Weight')
    
    exp_date_start = fields.Date(string='Start Date')
    exp_date_end = fields.Date(string='End Date')
    progress_planned = fields.Float(string='Scheduled Progress')
    progress_actual = fields.Float(string='Work Progress', compute='_compute_progress', store=True)
    date_start = fields.Date(string='Actual Start Date')
    date_end = fields.Date(string='Actual End Date')
    
    progress_ids = fields.One2many('project.task.progress', 'task_id', string='Task Progress')

    
class ProjectTaskProgress(models.Model):
    _name = 'project.task.progress'
    _description = 'Task Progress'
    
    name = fields.Char(string='Work Summary', required=True)
    task_id = fields.Many2one('project.task', string='Task', required=True)
    progress_unit = fields.Float(string='Units Completed')
    progress_day = fields.Float(string='Days Spent')
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    user_id = fields.Many2one('res.users', string='Done by', default=lambda self: self.env.uid, required=True)
