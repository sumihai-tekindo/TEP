from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo.tools.safe_eval import safe_eval


class SakitBerkepanjangan(models.Model):
	_name 	= 'hr.sakit.berkepanjangan'
	_rec_name = 'employee_id'


	name 		= fields.Char('Name')
	employee_id = fields.Many2one('hr.employee','Karyawan')
	date_start	= fields.Date('Tanggal Mulai Sakit')

	state 		= fields.Selection([('new','New'),
									('progress','Progress'),
									('finish','Finish')], default='new')



	@api.one
	def progress(self):
		self.state = 'progress'

	@api.one
	def finish(self):
		self.state = 'finish'

	@api.one
	def set_to_new(self):
		self.state = 'new'