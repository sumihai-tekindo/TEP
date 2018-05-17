from odoo import models,fields,api
	
class PurchaseOrder(models.Model):

	_inherit = 'purchase.order'

	project_id = fields.Many2one('project.project', string = "Project", required=True)
	task_id = fields.Many2one('project.task', string = "Task")
	department_id = fields.Many2one('hr.department', string = "Department")
	contact_person = fields.Char(string = "Contact Person")

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

class PurchaseOrderLine(models.Model):

	_inherit = 'purchase.order.line'

	spb_id = fields.Many2one('spb', string = "No SPB")

