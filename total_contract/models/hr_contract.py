from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime


class hr_contract(models.Model):
	_inherit = 'hr.contract'



	@api.onchange('trial_date_start','date_start')
	def onchange_date_start(self):
		employee_obj = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
		if self.employee_id.join_date_trigger == True:
			employee_obj.write({'join_date_trigger':False})
		else:
			employee_obj.write({'join_date_trigger':True})