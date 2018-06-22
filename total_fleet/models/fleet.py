from odoo import models, fields, api, _


class FleetVehicle(models.Model):
	_inherit = 'fleet.vehicle'



	machine_number 			= fields.Char('Machine Number')
	production_year			= fields.Char('Production Year')
	fuel_type = fields.Selection([('premium', 'Premium'),
								 ('pertamax', 'Pertamax'), 
								 ('petralite', 'Petralite'), 
								 ('diesel', 'Diesel'),
								 ('solar','Solar')], 'Fuel Type', help='Fuel Used by the vehicle')

	employee_id				= fields.Many2one('hr.employee','Person In Charge')





class FleetVehicle(models.Model):
	_inherit = 'fleet.vehicle.log.services'


	state 			= fields.Selection([('new','New'),
										('submitted','Submitted'),
										('approved','Approved'),
										('in_repair','In Repair'),
										('paid','Paid'),
										('rejected','Rejected')],'State', default="new")



	@api.one
	def submitted(self):
		self.state = 'submitted'

	@api.one
	def approved(self):
		self.state = 'approved'

	@api.one
	def repair(self):
		self.state = 'in_repair'

	@api.one
	def create_cash_register(self):
		self.state = 'paid'