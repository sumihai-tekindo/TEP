from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo.tools.safe_eval import safe_eval


class ListKost(models.Model):
	_name 	= 'list.kost'
	_rec_name = 'name'


	name 			= fields.Char('Name')
	date 			= fields.Date('Tanggal')
	pemilik			= fields.Char('Pemilik')
	employee_id		= fields.Many2one('hr.employee','Karyawan')
	biaya_kost		= fields.Float('Biaya Kost')
	start_date		= fields.Date('Start Date')
	end_date		= fields.Date('End Date')
