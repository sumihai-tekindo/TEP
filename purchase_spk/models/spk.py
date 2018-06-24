from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

    
class PurchaseSpk(models.Model):
    _name = 'purchase.spk'
    _description = 'SPK'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date_order desc, id desc'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.quantity, product=False, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })
            
    READONLY_STATES = {
        'open': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    name = fields.Char(string='Name', required=True, readonly=True, default='Draft SPK')
    parent_id = fields.Many2one('purchase.spk', string='Parent SPK', states=READONLY_STATES)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES)
    partner_ref = fields.Char(string='Vendor Reference', states=READONLY_STATES)
    project_id = fields.Many2one('project.project', string='Project', required=True, states=READONLY_STATES)
    task_id = fields.Many2one('project.task', string='Task', required=True, states=READONLY_STATES)
    date_order = fields.Date(string='Order Date', required=True, states=READONLY_STATES)
    order_line = fields.One2many('purchase.spk.line', 'order_id', string='Lines', states=READONLY_STATES)
    retention = fields.Float(string='Retention', states=READONLY_STATES)
    
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
        for order in self:
            if not order.name == 'Draft SPK':
                ctx = {
                    'ir_sequence_date': order.date_order,
                    'suffix': order.project_id.code or '',
                }
                order.name = self.env['ir.sequence'].with_context(ctx).next_by_code('spk')
            order.state = 'pm_approve'
    
    @api.multi
    def action_pm_approve(self):
        for order in self:
            order.state = 'open' if order.amount_total <= order.company_id.pmdir_treshhold_amount else 'dir_approve'
    
    @api.multi
    def action_dir_approve(self):
        for order in self:
            order.state = 'open'
    
    @api.multi
    def action_done(self):
        for order in self:
            order.state = 'done'
    
    @api.multi
    def action_cancel(self):
        for order in self:
            order.state = 'cancel'
    
    @api.multi
    def action_set_draft(self):
        for order in self:
            order.state = 'draft'
    
    @api.multi
    def action_unlock(self):
        for order in self:
            order.state = 'open'
    
    @api.onchange('project_id')
    def onchange_project_id(self):
        if not self.project_id:
            self.task_id = False
        return {'domain': {'task_id': [('project_id', '=', self.project_id.id)]}}
    
    
class PurchaseSpkLine(models.Model):
    _name = 'purchase.spk.line'
    _description = 'SPK Lines'

    @api.depends('quantity', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.quantity, product=False, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Description', required=True)
    order_id = fields.Many2one('purchase.spk', string='SPK')
    state = fields.Selection(related='order_id.state', store=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)
    quantity = fields.Float(string='Volume', digits=dp.get_precision('Product Unit of Measure'), required=True)
    uom_id = fields.Many2one('product.uom', string='UoM', required=True)
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'), required=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=[('active', '=', True)])
    company_id = fields.Many2one('res.company', 'Company', related='order_id.company_id', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', related='order_id.currency_id', readonly=True)
    
    progress_last = fields.Float(string='Last Progress', digits=dp.get_precision('Unit Price'), default=0.0)
    qty_last = fields.Float(string='Last Volume', digits=dp.get_precision('Product Unit of Measure'), default=0.0)
    price_total_last = fields.Float(string='Last Volume', digits=dp.get_precision('Unit Price'), default=0.0)
    amount_ret_last = fields.Float(string='Last Volume', digits=dp.get_precision('Unit Price'), default=0.0)
    amount_net_last = fields.Float(string='Last Volume', digits=dp.get_precision('Unit Price'), default=0.0)

    amount_ret_hold = fields.Float(string='Retention Held', digits=dp.get_precision('Unit Price'), default=0.0)
                
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)
