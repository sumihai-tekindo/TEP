
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, except_orm, Warning, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta




class PlafonMedical(models.Model):
	_name 	= 'hr.plafon.medical'

	name 			= fields.Char('Name')
	jabatan			= fields.Selection([('all','All'),
										('bod','BOD'),
										('manager','Manager'),
										('staff','Staff')],'Jabatan')
	percentage		= fields.Integer('Percentage')



	@api.multi
	def name_get(self):
		res = []
		for rec in self:
			if rec.jabatan == 'all':
				jabatan = 'All'
			elif rec.jabatan == 'bod':
				jabatan = 'BOD'
			elif rec.jabatan == 'manager':
				jabatan = 'Manager'
			else:
				jabatan = 'Staff'
			name = '' +rec.name + ' ' '/' + ' ' +jabatan
			res.append((rec.id, name))
		return res
