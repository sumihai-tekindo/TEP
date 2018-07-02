from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo.tools.safe_eval import safe_eval


class SewaKost(models.Model):
	_name 	= 'sewa.kost'
	_rec_name = 'name'


	name 			= fields.Char('Name')
	date 			= fields.Date('Tanggal')
	pemilik			= fields.Char('Nama Pemilik')
	alamat			= fields.Char('Alamat')
	no_ktp			= fields.Char('No.KTP')
	pekerjaan_pemilik	= fields.Char('Pekerjaan Pemilik')
	employee_id		= fields.Many2one('hr.employee','Penyewa')
	project_id		= fields.Many2one('project.project','Project')
	jabatan_id		= fields.Many2one('hr.job','Jabatan')
	biaya_kost		= fields.Float('Biaya Kost/Kamar')
	start_date		= fields.Date('Start Date')
	end_date		= fields.Date('End Date')
