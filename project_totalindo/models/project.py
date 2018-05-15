from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"
    
    @api.depends('employee_ids')
    def _user_ids(self):
        for project in self:
            user_ids = []
            for employee in project.employee_ids:
                if not employee.user_id:
                    raise UserError(_('Please set related user on employee %s') % (employee.name))
                user_ids.append(employee.user_id.id)
            if user_ids:
                project.user_ids = [(6, 0, user_ids)]
    
    @api.depends('name')
    def _first_contract_amount(self):
        for project in self:
            sale = self.env['sale.order'].search([('project_id', '=', project.analytic_account_id.id)], limit=1)
            project.first_contract_amount = sale.amount_total
    
    @api.depends('first_contract_amount', 'addendum_amount', 'budget_amount')
    def _contract_amount(self):
        for project in self:
            contract_amount = project.first_contract_amount + project.addendum_amount
            project.contract_amount = contract_amount
            est_profit_amount = contract_amount - project.budget_amount
            project.est_profit_amount = est_profit_amount
            amount_total = contract_amount + est_profit_amount
            project.est_margin_amount = est_profit_amount / amount_total * 100 if amount_total > 0.0 else 0.0
    
    @api.depends('budget_ids.planned_amount')
    def _budget_amount(self):
        for project in self:
            project.budget_amount = sum(project.budget_ids.mapped('planned_amount'))
    
    def _expense_ids(self):
        for project in self:
            domain = [('analytic_account_id.project_id', '=', project.id)]
            if project.exp_date_start:
                domain += [('date', '>=', project.exp_date_start)]
            if project.exp_date_end:
                domain += [('date', '<=', project.exp_date_end)]
            if project.move_filter:
                domain += ['|', '|', ('name', 'like', project.move_filter), ('ref', 'like', project.move_filter),
                           ('move_id.name', 'like', project.move_filter)]
            line_ids = self.env['account.move.line'].search(domain).ids
            if line_ids:
                self.expense_ids = [(6, 0, line_ids)]
    
    budget_ids = fields.One2many('account.analytic.account', 'project_id', string='Budgets')
    street = fields.Char('Address')
    street2 = fields.Char(string='Address')
    province_id = fields.Char('Province')
    zip = fields.Char(string='ZIP')
    city_id = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    manager_id = fields.Many2one('res.users', string='Project Manager')
    tender_amount = fields.Monetary(string='Tender Value', digits=dp.get_precision('Product Price'))
    dp_amount = fields.Monetary(string='DP', digits=dp.get_precision('Product Price'))
    catering = fields.Boolean(string='Catering')
    
    user_ids = fields.Many2many('res.users', 'project_users_rel', 'project_id', 'user_id', string='Team', compute='_user_ids', store=True)
    employee_ids = fields.Many2many('hr.employee', 'project_employee_rel', 'project_id', 'employee_id', string='Team')
    
    first_contract_amount = fields.Monetary(string='Total Contract 1st Value', digits=dp.get_precision('Product Price'),
        compute='_first_contract_amount', store=True)
    addendum_amount = fields.Monetary(string='Total Addendum ', digits=dp.get_precision('Product Price'))
    contract_amount = fields.Monetary(string='Total Contract', digits=dp.get_precision('Product Price'),
        compute='_contract_amount', store=True)
    budget_amount = fields.Monetary(string='Total Budget', digits=dp.get_precision('Product Price'),
        compute='_budget_amount', store=True)
    est_profit_amount = fields.Monetary(string='Estimated Profit', digits=dp.get_precision('Product Price'),
        compute='_contract_amount', store=True)
    est_margin_amount = fields.Float(string='Estimated Margin', digits=dp.get_precision('Discount'),
        compute='_contract_amount', store=True)
    
    document_ids = fields.One2many('project.document', 'project_id', string='References')
    
    exp_date_start = fields.Date(string='From Date')
    exp_date_end = fields.Date(string='To Date')
    move_filter = fields.Char(string='Transaction No')
    expense_ids = fields.Many2many('account.move.line', 'project_move_line_rel', 'project_id', 'move_line_id',
        string='Expenses', compute='_expense_ids')
    
    location_id = fields.Many2one('stock.location', string='Project Location', domain=[('usage', '=', 'internal')])
    
    @api.multi
    def budget_tree_view(self):
        self.ensure_one()
        domain = [('project_id', '=', self.id)]
        return {
            'name': _('Budget'),
            'domain': domain,
            'res_model': 'account.analytic.account',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d, 'group_by': ('level_1_id','level_2_id','level_3_id')}" % (self.id)
        }

    @api.multi
    def picking_type_kanban_view(self):
        self.ensure_one()
        domain = [('project_id', '=', self.id)]
        return {
            'name': _('Inventory'),
            'domain': domain,
            'res_model': 'stock.picking.type',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d}" % (self.id)
        }

    @api.multi
    def contract_tree_view(self):
        self.ensure_one()
        domain = [('project_id', '=', self.analytic_account_id.id)]
        return {
            'name': _('Contract'),
            'domain': domain,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d}" % (self.id)
        }

    @api.multi
    def purchase_tree_view(self):
        self.ensure_one()
        domain = [('project_id', '=', self.id)]
        return {
            'name': _('PO'),
            'domain': domain,
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d}" % (self.id)
        }

    @api.multi
    def spk_tree_view(self):
        self.ensure_one()
        domain = [('project_id', '=', self.id)]
        return {
            'name': _('SPK'),
            'domain': domain,
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d}" % (self.id)
        }

    @api.multi
    def cust_inv_tree_view(self):
        self.ensure_one()
        inv_ids = self.env['account.invoice.line'].search([('account_analytic_id.project_id', '=', self.id)]).mapped('invoice_id')
        domain = [('id', 'in', inv_ids.ids), ('type', '=', 'out_invoice')]
        return {
            'name': _('Customer Invoice'),
            'domain': domain,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d}" % (self.id)
        }

    @api.multi
    def supp_inv_tree_view(self):
        self.ensure_one()
        inv_ids = self.env['account.invoice.line'].search([('account_analytic_id.project_id', '=', self.id)]).mapped('invoice_id')
        domain = [('id', 'in', inv_ids.ids), ('type', '=', 'in_invoice')]
        return {
            'name': _('Supplier Invoice'),
            'domain': domain,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_project_id': %d}" % (self.id)
        }
