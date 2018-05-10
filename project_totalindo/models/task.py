from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    @api.depends('exp_date_start', 'exp_date_end')
    def _compute_progress_planned(self):
        for task in self:
            if task.exp_date_start and task.exp_date_end:
                time_date_start = datetime.strptime(task.exp_date_start, '%Y-%m-%d')
                time_date_end = datetime.strptime(task.exp_date_end, '%Y-%m-%d')
                time_date = datetime.today()
                task.progress_planned = float((time_date - time_date_start).days) / float((time_date_end - time_date_start).days) * 100
                
    @api.depends('unit_planned', 'progress_ids.progress_unit')
    def _compute_progress_actual(self):
        for task in self:
            task.progress_actual = sum([progress.progress_unit for progress in task.progress_ids]) / task.unit_planned * 100 if task.unit_planned > 0.0 else 0.0
    
    @api.depends('amount')
    def _compute_weight(self):
        for task in self:
            task_ids = self.search([('project_id', '=', task.project_id.id), ('stage_id.exclude_weight', '=', False)])
            total_amount = sum([task_id.amount for task_id in task_ids])
            task.weight = task.amount / total_amount * 100 if total_amount != 0.0 else 0.0
    
    code = fields.Char(string='Code')
    day_planned = fields.Float(string='Planned Days')
    unit_planned = fields.Float(string='Target Units')
    uom_id = fields.Many2one('product.uom', string='UoM')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='UoM')
    amount = fields.Monetary(string='RAB Value')
    weight = fields.Float(string='Weight', compute='_compute_weight', store=False)
    
    exp_date_start = fields.Date(string='Start Date')
    exp_date_end = fields.Date(string='End Date')
    progress_planned = fields.Float(string='Scheduled Progress', compute='_compute_progress_planned')
    progress_actual = fields.Float(string='Work Progress', compute='_compute_progress_actual', store=True)
    date_start = fields.Date(string='Actual Start Date')
    date_end = fields.Date(string='Actual End Date')
    
    progress_ids = fields.One2many('project.task.progress', 'task_id', string='Task Progress')

    
class ProjectTaskProgress(models.Model):
    _name = 'project.task.progress'
    _description = 'Task Progress'
    
    @api.depends('task_id.exp_date_start', 'task_id.exp_date_end', 'task_id.weight', 'date')
    def _progress_expected(self):
        for progress in self:
            if progress.task_id.exp_date_start and progress.task_id.exp_date_end and progress.date:
                time_date_start = datetime.strptime(progress.task_id.exp_date_start, '%Y-%m-%d')
                time_date_end = datetime.strptime(progress.task_id.exp_date_end, '%Y-%m-%d')
                time_date = datetime.strptime(progress.date, '%Y-%m-%d')
                progress.progress_expected = float((time_date - time_date_start).days) / float((time_date_end - time_date_start).days) * progress.task_id.weight
    
    name = fields.Char(string='Work Summary', required=True)
    task_id = fields.Many2one('project.task', string='Task', required=True)
    progress_unit = fields.Float(string='Units Completed')
    progress_day = fields.Float(string='Days Spent')
    progress_expected = fields.Float(string='Expected Progress', compute='_progress_expected', store=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    user_id = fields.Many2one('res.users', string='Done by', default=lambda self: self.env.uid, required=True)

    
class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    
    exclude_weight = fields.Boolean(string='Exclude in Weight Computation')
    
