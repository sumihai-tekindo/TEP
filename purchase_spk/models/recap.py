from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

    
class RecapMandor(models.Model):
    _name = 'recap.mandor'
    _description = 'Recap'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date desc, id desc'

    @api.depends('opname_line.amount_total')
    def _amount_all(self):
        for recap in self:
            amount_total = 0.0
            amount_total = sum(line.amount_total for line in recap.opname_line)
            recap.update({
                'amount_total': recap.currency_id.round(amount_total),
            })
            
    READONLY_STATES = {
        'open': [('readonly', True)],
        'qs_approve': [('readonly', True)],
        'pm_approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    name = fields.Char(string='Name', required=True, readonly=True, default='Draft Recap')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES)
    project_id = fields.Many2one('project.project', string='Project', required=True, states=READONLY_STATES)
    date = fields.Date(string='Order Date', required=True, states=READONLY_STATES, default=fields.Date.context_today)
    opname_line = fields.Many2many('opname.mandor', string='Lines', states=READONLY_STATES)
    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    user_id = fields.Many2one('res.users', string='Done by', default=lambda self: self.env.uid, required=True, states=READONLY_STATES)

    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    
    state = fields.Selection([('draft', 'Draft'),
                              ('qs_approve', 'QS Approval'),
                              ('pm_approve', 'PM Approval'),
                              ('open', 'In Progress'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')], string='State', default='draft', readonly=True, copy=False, index=True)
    notes = fields.Text(string='Terms and Conditions')
    
    @api.multi
    def action_confirm(self):
        for recap in self:
            if recap.name == 'Draft Recap':
                ctx = {
                    'ir_sequence_date': recap.date,
                    'prefix': recap.partner_id.ref or '',
                }
                recap.name = self.env['ir.sequence'].with_context(ctx).next_by_code('recap')
            recap.state = 'qs_approve'
    
    @api.multi
    def action_qs_approve(self):
        for recap in self:
            recap.state = 'pm_approve'
    
    @api.multi
    def action_pm_approve(self):
        for recap in self:
            recap.state = 'open'
    
    @api.multi
    def action_done(self):
        for recap in self:
            recap.state = 'done'
    
    @api.multi
    def action_cancel(self):
        for recap in self:
            recap.state = 'cancel'
    
    @api.multi
    def action_set_draft(self):
        for recap in self:
            recap.state = 'draft'
    
    @api.multi
    def action_unlock(self):
        for recap in self:
            recap.state = 'open'
    
#     @api.onchange('project_id')
#     def onchange_project_id(self):
#         if not self.project_id:
#             self.task_id = False
#         return {'domain': {'task_id': [('project_id', '=', self.project_id.id)]}}
    
    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id and not self.partner_id:
            raise UserError(_('Please set vendor first.'))
        self.recap_line = []
        if not self.partner_id:
            return {}
        # set line values
        temp_opnames = self.env['opname.mandor'].search([('partner_id', '=', self.partner_id.id),
                                                         ('project_id', '=', self.project_id.id)], order='sequence desc')
        opname_ids = []
        for opname in temp_opnames:
            if opname.spk_id.id not in [op.spk_id.id for op in opname_ids]:
                opname_ids.append(opname)
        self.opname_line = [opname.id for opname in opname_ids]
#         return {'value': {
#             'opname_line': [(6, 0, [opname.id for opname in opname_ids])],
#         }}
    
    @api.model
    def create(self, vals):
        if vals.get('opname_line'):
           vals['opname_line'] = [(6, 0, [opname[1] for opname in vals.get('opname_line') if opname[0] == 1])]
        return super(RecapMandor, self).create(vals)
    
    @api.multi
    def write(self, vals):
        if vals.get('opname_line'):
            vals['opname_line'] = [(6, 0, [opname[1] for opname in vals.get('opname_line') if opname[0] == 1])]
        return super(RecapMandor, self).write(vals)


class RecapMandorLine(models.Model):
    _name = 'recap.mandor.line'
    _description = 'Recap Lines'

    @api.depends('progress_upnow', 'ret_hold')
    def _compute_amount(self):
        for line in self:
            price_spk = line.price_spk
            price_total_spk = line.price_total_spk
            retention = line.recap_id.spk_id.retention
            ret_hold = line.ret_hold
            qty_spk = line.qty_spk
            progress_upnow = line.progress_upnow
            progress = progress_upnow - line.progress_last
            qty_upnow = qty_spk * progress_upnow / 100
            qty = qty_upnow - line.qty_last
            price_total = qty * price_spk
            amount_ret_upnow = progress_upnow * retention * price_total_spk / 100 / 100 if ret_hold else 0.0
            amount_ret = progress * retention * price_total_spk / 100 / 100 if ret_hold else 0.0
            price_total_upnow = qty_upnow * price_spk
            amount_ret_release = line.spk_line_id.amount_ret_hold if not ret_hold else 0.0
            qty_balance = qty_spk - qty_upnow
            line.update({
                'qty': qty,
                'progress': progress,
                'qty_upnow': qty_upnow,
                'price_total': price_total,
                'amount_ret': amount_ret,
                'amount_net': price_total - amount_ret,
                'price_total_upnow': price_total_upnow,
                'amount_ret_upnow': amount_ret_upnow,
                'amount_net_upnow': price_total_upnow - amount_ret_upnow,
                'amount_ret_release': amount_ret_release,
                'qty_balance': qty_balance,
            })
            
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Description', required=True)
    recap_id = fields.Many2one('recap.mandor', string='Recap')
    spk_line_id = fields.Many2one('purchase.spk.line', string='SPK Line')
    state = fields.Selection(related='recap_id.state', store=True)
    company_id = fields.Many2one('res.company', 'Company', related='recap_id.company_id', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', related='recap_id.currency_id', readonly=True)
#     product_id = fields.Many2one('product.product', string='Product', required=True)
    uom_id = fields.Many2one('product.uom', string='UoM', required=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)
    
    qty_spk = fields.Float(string='Vol SPK', digits=dp.get_precision('Qty'), readonly=True)
    price_spk = fields.Float(string='Price SPK', digits=dp.get_precision('Product Price'), readonly=True)
    price_total_spk = fields.Monetary(string='Total', readonly=True)
    
    progress_last = fields.Float(string='Progress', digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    qty_last = fields.Float(string='Volume', digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    price_total_last = fields.Monetary(string='Total', readonly=True)
    amount_ret_last = fields.Monetary(string='Ret Amount', readonly=True)
    amount_net_last = fields.Monetary(string='Net Amount', readonly=True)
    
    amount_ret_release = fields.Monetary(compute='_compute_amount', string='Ret Release Amount', store=True)
    
    ret_hold = fields.Boolean(string='Hold Ret')
    
    progress = fields.Float(compute='_compute_amount', string='Progress', digits=dp.get_precision('Product Unit of Measure'), store=True)
    qty = fields.Float(compute='_compute_amount', string='Volume', digits=dp.get_precision('Product Unit of Measure'), store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    amount_ret = fields.Monetary(compute='_compute_amount', string='Ret Amount', store=True)
    amount_net = fields.Monetary(compute='_compute_amount', string='Net Amount', store=True)
    
    progress_upnow = fields.Float(string='Progress', digits=dp.get_precision('Product Unit of Measure'), required=True)
    qty_upnow = fields.Float(compute='_compute_amount', string='Volume', digits=dp.get_precision('Product Unit of Measure'), store=True)
    price_total_upnow = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    amount_ret_upnow = fields.Monetary(compute='_compute_amount', string='Ret Amount', store=True)
    amount_net_upnow = fields.Monetary(compute='_compute_amount', string='Net Amount', store=True)
    
    qty_balance = fields.Float(compute='_compute_amount', string='Balance Vol', digits=dp.get_precision('Product Unit of Measure'), store=True)
    amount_ret_exc = fields.Monetary(string='Exc Ret Amount')
    
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)
