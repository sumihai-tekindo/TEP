from datetime import date
# from datetime import datetime
# from datetime import timedelta
# from dateutil import relativedelta
# import time

from odoo import models, fields, api, _
# from odoo.exceptions import UserError
# from odoo.tools.safe_eval import safe_eval as eval
# from odoo.tools.translate import _


class ProjectTaskUpdate(models.Model):
    _name = 'project.task.update'
    _inherit = ['mail.thread']
    _description = "Update Sacme"
    _order = "date desc, id desc"

    sacme_id = fields.Many2one('project.project', string='Sacme', required=True,
                               domain=[('account_class', '=', 'work_package'), ('geo_type', '=', 'point')],
                               readonly=True, states={'draft': [('readonly', False)]})
    task_id = fields.Many2one('project.task', string='Task', required=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved')], string='State', default='draft',
                             track_visibility='onchange')
    date = fields.Date(string='Date', required=True, readonly=True, states={'draft': [('readonly', False)]})
    date_approved = fields.Date(string='Approval Date', readonly=True, track_visibility='onchange')
    stage_id = fields.Many2one('project.task.type', string='Stage', copy=False, 
                               required=True, readonly=True, states={'draft': [('readonly', False)]})
#     attachement = fields.Binary(string='Attachement')
    
    @api.model
    def create(self, vals):
        import pdb;pdb.set_trace()
        return super(ProjectTaskUpdate, self).create(vals)
        
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.task_id.name + ', ' + record.sacme_id.name))
        return res
    
    @api.multi
    def action_approve(self):
        self.env['project.task'].browse(self.task_id.id).stage_id = self.stage_id.id
        self.date_approved = fields.Date.context_today(self)
        # update attachement
        update_ats = self.env['ir.attachment'].search([('res_model', '=', 'project.task.update'), ('res_id', '=', self.id)])
        for att in update_ats:
            att.copy({'name': att.name, 'res_model': 'project.task', 'res_id': self.task_id.id})
        self.state = 'approved'
    
    @api.onchange('sacme_id')
    def on_change_sacme_id(self):
        self.task_id = False
     
