from odoo import models,fields,api, _
from odoo.exceptions import UserError, AccessError, ValidationError
	
class PurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	project_id 		= fields.Many2one('project.project', string = "Project", required=True)
	task_id 		= fields.Many2one('project.task', string = "Task")
	department_ids 	= fields.Many2many('hr.department', string = "Department", compute="get_user_spb")
	user_ids 		= fields.Many2many('res.users', string = "Contact Person", compute="get_user_spb")

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('po.sequence.inherit') or '/'
			code = self.env['project.project'].browse(vals['project_id']).code
			vals['name'] = vals['name'][:10]+'/TEP-'+code+vals['name'][10:]
		return super(PurchaseOrder, self).create(vals)

	@api.model
	def _prepare_picking(self):
		if not self.group_id:
			self.group_id = self.group_id.create({
				'name': self.name,
				'partner_id': self.partner_id.id
			})
		if not self.partner_id.property_stock_supplier.id:
			raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
		return {
			'picking_type_id': self.picking_type_id.id,
			'partner_id': self.partner_id.id,
			'date': self.date_order,
			'origin': self.name,
			'location_dest_id': self._get_destination_location(),
			'location_id': self.partner_id.property_stock_supplier.id,
			'company_id': self.company_id.id,
			'project_id': self.project_id.id,
		}

	@api.multi
	def button_confirm(self):
		for order in self:
			if order.state not in ['draft', 'sent']:
				continue
			order._add_supplier_to_product()
			# Deal with double validation process
			if (order.company_id.po_double_validation == 'three_step'\
					and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_third_validation_amount, order.currency_id))\
				or order.user_has_groups('purchase.group_purchase_direktur'):
				order.button_approve()
			elif order.company_id.po_double_validation == 'one_step'\
					or (order.company_id.po_double_validation == 'two_step'\
						and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
					or order.user_has_groups('purchase.group_purchase_manager'):
				order.button_approve()
			else:
				order.write({'state': 'to approve'})
		return True

	@api.depends('order_line.spb_id')
	def get_user_spb(self):
		cp = []
		department = []
		for order in self:
			for line in order.order_line:
				cp.append(line.spb_id.create_uid.id)
				department.append(line.spb_id.departemen_id.id)
		self.user_ids = cp
		self.department_ids = department

class PurchaseOrderLine(models.Model):

	_inherit = 'purchase.order.line'

	spb_id = fields.Many2one('spb', string = "No SPB")


	@api.onchange('spb_id')
	def onchange_product_id_spb(self):
		self.ensure_one()
		product_ids = []
		lines = self.env['spb.line'].search([('spb_id','=',self.spb_id.id),('outstanding_spb','>',0.0)])
		product_ids = [x.product_id.id for x in lines if x.product_id]
		return  {'domain':{'product_id':[('id','in', (product_ids))]}}

	@api.onchange('product_id')
	def onchange_product_id(self):
		self.ensure_one()
		super(PurchaseOrderLine,self).onchange_product_id()
		self.product_qty =  self.env['spb.line'].search([('spb_id','=',self.spb_id.id),('product_id','=',self.product_id.id)]).outstanding_spb