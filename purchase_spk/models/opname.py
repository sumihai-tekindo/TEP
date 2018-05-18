from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

    
class OpnameMandor(models.Model):
    _name = 'opname.mandor'
    _description = 'Opname'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date desc, id desc'

    @api.depends('opname_line.price_total')
    def _amount_all(self):
        for opname in self:
            amount_untaxed = amount_tax = 0.0
            for line in opname.opname_line:
                amount_total += line.price_subtotal
            opname.update({
                'amount_total': opname.currency_id.round(amount_total),
            })
            
    READONLY_STATES = {
        'open': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    name = fields.Char(string='Name', required=True, readonly=True, default='Draft Opname')
    spk_id = fields.Many2one('purchase.spk', string='SPK', required=True, states=READONLY_STATES)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES)
    partner_ref = fields.Char(string='Vendor Reference', states=READONLY_STATES)
    project_id = fields.Many2one('project.project', string='Project', required=True, states=READONLY_STATES)
    task_id = fields.Many2one('project.task', string='Task', required=True, states=READONLY_STATES)
    date = fields.Date(string='Order Date', required=True, states=READONLY_STATES)
    sequence = fields.Date(string='Opname Sequence', readonly=True)
    opname_line = fields.One2many('opname.mandor.line', 'opname_id', string='Lines', states=READONLY_STATES)
    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    user_id = fields.Many2one('res.users', string='Done by', default=lambda self: self.env.uid, required=True, states=READONLY_STATES)

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    
    state = fields.Selection([('draft', 'Draft'),
                              ('pm_approve', 'PM Approval'),
                              ('dir_approve', 'Director Approval'),
                              ('open', 'In Progress'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')], string='State', default='draft', readonly=True, copy=False, index=True)
    notes = fields.Text(string='Terms and Conditions')
    
    @api.multi
    def action_confirm(self):
        for opname in self:
            opname.state = 'pm_approve' if opname.amount_total <= opname.company_id.pmdir_treshhold_amount else 'dir_approve'
    
    @api.multi
    def action_pm_approve(self):
        for opname in self:
            opname.state = 'open'
    
    @api.multi
    def action_dir_approve(self):
        for opname in self:
            opname.state = 'open'
    
    @api.multi
    def action_done(self):
        for opname in self:
            opname.state = 'done'
    
    @api.multi
    def action_cancel(self):
        for opname in self:
            opname.state = 'cancel'
    
    @api.multi
    def action_set_draft(self):
        for opname in self:
            opname.state = 'draft'
    
    @api.multi
    def action_unlock(self):
        for opname in self:
            opname.state = 'open'
    
    @api.onchange('project_id')
    def onchange_project_id(self):
        if not self.project_id:
            self.task_id = False
        return {'domain': {'task_id': [('project_id', '=', self.project_id.id)]}}
    
    
class OpnameMandorLine(models.Model):
    _name = 'opname.mandor.line'
    _description = 'Opname Lines'

    @api.depends('quantity', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.opname_id.currency_id, line.quantity, product=False, partner=line.opname_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Description', required=True)
    opname_id = fields.Many2one('opname.mandor', string='Opname')
    state = fields.Selection(related='opname_id.state', store=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)
    quantity = fields.Float(string='Volume', digits=dp.get_precision('Product Unit of Measure'), required=True)
    uom_id = fields.Many2one('product.uom', string='UoM', required=True)
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'), required=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=[('active', '=', True)])
    company_id = fields.Many2one('res.company', 'Company', related='opname_id.company_id', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', related='opname_id.currency_id', readonly=True)
    
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)
