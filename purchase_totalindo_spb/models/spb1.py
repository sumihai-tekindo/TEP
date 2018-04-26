from odoo import models, fields, api
# from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp


class SpbHeader(models.Model):
	_name = 'purchasetotalindo.spbheader'

	READONLY_STATES = {
		'approve': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	name = fields.Char(default="New", state=READONLY_STATES, string="Number SPB", required=True)
	date_spb = fields.Date(default=fields.Date.today, state=READONLY_STATES, string="Date SPB", required=True)
	project_id = fields.Many2one('project.project', state=READONLY_STATES, string="Project", required=True)
	department_id = fields.Many2one('hr.department', state=READONLY_STATES, string="Department", required=True)
	budget = fields.Selection([('yes', 'Yes'), ('no', 'No')], state=READONLY_STATES, string="Budgeted")
	description = fields.Char(state=READONLY_STATES, string="Description")
	date_required = fields.Date(default=fields.Date.today, state=READONLY_STATES, string="Date Required", required=True)
	state = fields.Selection([('draft', 'Draft'),('confirm', 'Confirm'),('approve', 'Approve'),('done', 'Done'),('cancel', 'Cancel')], default="draft", string="Status")
	spbdetail_ids = fields.One2many('purchasetotalindo.spbdetail', 'spbheader_id', state=READONLY_STATES)
	partner_id = fields.Many2one('res.partner', string="Vendor", state=READONLY_STATES)

	@api.multi
	def button_confirm(self):
		self.write({'state': 'confirm'})

	@api.multi
	def button_approve(self):
		self.ensure_one()
		order_vals = {
			'partner_id':self.partner_id.id,
			'date_order':fields.Datetime.now(),
			'date_planned':fields.Datetime.now(),
		}
		order = self.env['purchase.order'].create(order_vals)
		new_lines = self.env['purchase.order.line']
		for line in self.spbdetail_ids:

			line_vals = {
				'product_id': line.product_id.id,
			}
			x = new_lines.new(line_vals)
			x.onchange_product_id()
			new_lines += x
		order.order_line = new_lines
			# self.write({'state': 'approve'})

	@api.multi
	def button_sendtodraft(self):
		self.write({'state': 'draft'})

	@api.multi
	def button_cancel(self):
		self.write({'state': 'cancel'})

	@api.multi
	def button_createpo(self):
		self.write({'state': 'done'})

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('purchasetotalindo.spb') or '/'
		return super(spb_header, self).create(vals)

	@api.multi
	def unlink(self):
		for order in self:
			if order.state in ('approve', 'done'):
				raise UserError(_('You cannot delete a approved SPB.'))
		return super(spb_header, self).unlink()
		
class SpbDetail(models.Model):
	_name = 'purchasetotalindo.spbdetail'

	name = fields.Text(string="Description")
	product_id = fields.Many2one('product.product', string="Product", required=True)
	product_uom = fields.Many2one('product.uom', string="Unit Of Product")
	quantity_order = fields.Float(digits=dp.get_precision('Product Unit of Measure'), string="Number Of Requests", required=True)
	coa_budget = fields.Float(digits=dp.get_precision('Product Unit of Measure'), string="COA Budget")
	quantity_transfer = fields.Float(digits=dp.get_precision('Product Unit of Measure'), string="Quantity Transfer", readonly=True)
	quantity_po = fields.Float(digits=dp.get_precision('Product Unit of Measure'), string="Quantity PO", readonly=True, compute="compute_po")
	outstanding_spb = fields.Float(digits=dp.get_precision('Product Unit of Measure'), string="Outstanding SPB", readonly=True, compute='sum_quantity_outstanding_spb')
	spbheader_id = fields.Many2one('purchasetotalindo.spbheader')
	state = fields.Selection(related = "spbheader_id.state", store=True, default="draft", string="Status")

	@api.depends('quantity_order','quantity_transfer','quantity_po')
	def sum_quantity_outstanding_spb(self):
		for record in self:
			record.outstanding_spb = record.quantity_order-(record.quantity_transfer+record.quantity_po) 

	@api.onchange('product_id')
	def onchange_description_product(self):
		result = {}
		if not self.product_id:
			return result

		self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
		result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
		product_lang = self.product_id.with_context(
			lang=self.env.user.lang
		)
		self.name = product_lang.display_name

		return result

	@api.multi
	def compute_po(self):
		for record in self:
			x = self.env['purchase.order.line'].search([('spb_id','=',record.spbheader_id.id),('product_id','=',record.product_id.id)], limit=1)
			record.quantity_po=x
			print(record.quantity_po)

class spb_wizard(models.TransientModel):
	_name = 'purchasetotalindo.spbwizard'

	name = fields.Char()
	pilihan_wizard = fields.Selection([('po','Purchase Order'),('io','Inventory Order')])
	buat_baru = fields.Selection([('yes','Yes'),('no','No')])
	add_po = fields.Many2one('purchase.order', )
