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
    
    @api.multi
    def _compute_practical_amount(self):
        for analytic in self:
            result = 0.0
            self.env.cr.execute("""
                SELECT SUM(balance)
                FROM account_move_line
                WHERE analytic_account_id=%s""",
            (analytic.id,))
            result = self.env.cr.fetchone()[0] or 0.0
            analytic.practical_amount = -result
            analytic.balance_amount = analytic.planned_amount + result
    
    @api.multi
    def _compute_theoritical_amount(self):
        today = fields.Datetime.now()
        for line in self:
            # Used for the report

            if self.env.context.get('wizard_date_from') and self.env.context.get('wizard_date_to'):
                date_from = fields.Datetime.from_string(self.env.context.get('wizard_date_from'))
                date_to = fields.Datetime.from_string(self.env.context.get('wizard_date_to'))
                if date_from < fields.Datetime.from_string(line.date_from):
                    date_from = fields.Datetime.from_string(line.date_from)
                elif date_from > fields.Datetime.from_string(line.date_to):
                    date_from = False

                if date_to > fields.Datetime.from_string(line.date_to):
                    date_to = fields.Datetime.from_string(line.date_to)
                elif date_to < fields.Datetime.from_string(line.date_from):
                    date_to = False

                theo_amt = 0.00
                if date_from and date_to:
                    line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(line.date_from)
                    elapsed_timedelta = date_to - date_from
                    if elapsed_timedelta.days > 0:
                        theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
            else:
                line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(line.date_from)
                elapsed_timedelta = fields.Datetime.from_string(today) - (fields.Datetime.from_string(line.date_from))

                if elapsed_timedelta.days < 0:
                    # If the budget line has not started yet, theoretical amount should be zero
                    theo_amt = 0.00
                elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(line.date_to):
                    # If today is between the budget line date_from and date_to
                    theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                else:
                    theo_amt = line.planned_amount

            line.theoritical_amount = theo_amt

    @api.multi
    def _compute_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0) / line.theoritical_amount) * 100
            else:
                line.percentage = 0.00
    
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    planned_amount = fields.Float('Planned Amount', required=True, digits=0)
    practical_amount = fields.Float(compute='_compute_practical_amount', string='Actual Amount', digits=0)
    balance_amount = fields.Float(compute='_compute_practical_amount', string='Balance Amount', digits=0)
    level_3_id = fields.Many2one('budget.level.three', string="Level 3", required=True)
    level_2_id = fields.Many2one('budget.level.two', string="Level 2", related="level_3_id.level_2_id", readonly=True, store=True)
    level_1_id = fields.Many2one('budget.level.one', string="Level 1", related="level_3_id.level_2_id.level_1_id", readonly=True, store=True)
#     theoritical_amount = fields.Float(compute='_compute_theoritical_amount', string='Theoretical Amount', digits=0)
#     percentage = fields.Float(compute='_compute_percentage', string='Achievement')

class AccountBudgetLog(models.Model):
    _name = 'account.budget.log'
    _description = 'Budget Log'
    
    name = fields.Integer(string='Revision')
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic')
    amount = fields.Float(string='Amount')


class BudgetLevelOne(models.Model):
    _name = 'budget.level.one'
    _description = 'Budget Level 1'

    name = fields.Char(string='Name', required=True)


class BudgetLevelTwo(models.Model):
    _name = 'budget.level.two'
    _description = 'Budget Level 2'

    name = fields.Char(string='Name', required=True)
    level_1_id = fields.Many2one('budget.level.one', string="Level 1")


class BudgetLevelThree(models.Model):
    _name = 'budget.level.three'
    _description = 'Budget Level 3'

    name = fields.Char(string='Name', required=True)
    level_2_id = fields.Many2one('budget.level.two', string="Level 2")

