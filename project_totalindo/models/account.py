# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2011-2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    READONLY_STATES = {
        'normal': [('readonly', True)],
        'done': [('readonly', True)],
        'blocked': [('readonly', True)],
    }
    state = fields.Selection(related='project_id.state', store=True, readonly=True)
    planned_amount = fields.Float('Planned Amount', required=True, digits=0, states=READONLY_STATES)
    project_id = fields.Many2one('project.project', string='Project', related='level_3_id.level_2_id.level_1_id.project_id',
        store=True, readonly=True)
    revision = fields.Integer(string='Revision', default=0)
    log_ids = fields.One2many('account.budget.log', 'analytic_id', string="Log", readonly=True)

    @api.multi
    def action_log(self):
        for this in self:
            self.env['account.budget.log'].create({
                'name': this.revision,
                'analytic_id': this.id,
                'amount': this.planned_amount,
            })
            this.revision += 1
        return True

class BudgetLevelOne(models.Model):
    _inherit = 'budget.level.one'
    
    project_id = fields.Many2one('project.project', string='Project', required=True) 
    
