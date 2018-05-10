from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

    
class PurchaseSpk(models.Model):
    _name = 'purchase.spk'
    _description = 'SPK'

    @api.depends('line_ids.price_total')
    def _amount_all(self):
        for spk in self:
            amount_untaxed = amount_tax = 0.0
            for line in spk.line_ids:
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
    
    name = fields.Char(string='Name', required=True, readonly=True)
    parent_id = fields.Many2one('purchase.spk', string='Parent SPK', states=READONLY_STATES)
    partner_id = fields.Many2one('res.partner', string='Vendor', states=READONLY_STATES)
    vendor_ref = fields.Char(string='Vendor Reference', states=READONLY_STATES)
    project_id = fields.Many2one('project.project', string='Project', states=READONLY_STATES)
    task_id = fields.Many2one('project.task', string='Task', states=READONLY_STATES)
    date = fields.Date(string='Order Date', states=READONLY_STATES)
    line_ids = fields.One2many('purchase.spk.line', 'spk_id', string='Lines', states=READONLY_STATES)
    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    user_id = fields.Many2one('res.users', string='Done by', default=lambda self: self.env.uid, required=True, states=READONLY_STATES)

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    
    state = fields.Selection([('draft','Draft'),
                              ('pm_approve', 'PM Approval'),
                              ('dir_approve', 'Director Approval'),
                              ('open', 'In Progress'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled'),], string='State', readonly=True)

    @api.multi
    def action_confirm(self):
        for spk in self:
            spk.state = 'pm_approve'
    
class PurchaseSpkLine(models.Model):
    _name = 'purchase.spk.line'
    _description = 'SPK Lines'

    @api.depends('quantity', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.spk_id.currency_id, line.quantity, product=False, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    name = fields.Char(string='Description', required=True)
    spk_id = fields.Many2one('purchase.spk', string='SPK')
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    quantity = fields.Float(string='Volume', digits=dp.get_precision('Product Unit of Measure'))
    uom_id = fields.Many2one('product.uom', string='UoM')
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
    taxes_ids = fields.Many2many('account.tax', string='Taxes', domain=[('active', '=', True)])
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)
