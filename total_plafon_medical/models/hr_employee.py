from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime


class hr_employee(models.Model):
	_inherit = 'hr.employee'


	@api.one
	def _get_trigger(self):
		datetimeFormat = '%Y-%m-%d'
		saldo = 0
		tahun_param = []
		ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
		today = fields.Date.today()
		prof_data_permanen = self.env['hr.employee.category'].search([('name','=','Permanen')])
		prof_data_kontrak = self.env['hr.employee.category'].search([('name','=','Kontrak')])
		medical_obj = self.env['hr.employee.plafon.medical']
		if prof_data_permanen in self.category_ids or prof_data_kontrak in self.category_ids:
			contract_data = self.env['hr.contract'].search([('employee_id','=',self.id),('state','=','open')])
			if not contract_data:
				self.medical_trigger = False
			else:
				self.medical_trigger = True
				join_date_formatted = datetime.strptime(self.join_date, datetimeFormat)
				today_formatted = datetime.strptime(today,datetimeFormat)
				end_year_formatted = datetime.strptime(str(ending_day_of_current_year),datetimeFormat)
				bulan_berjalan = str((end_year_formatted-join_date_formatted).days)
				bulan_berjalan_int = int(bulan_berjalan) / 30
				if int(bulan_berjalan_int) >= 12:
					saldo = contract_data.wage
				else:
					saldo = float(bulan_berjalan_int)/12 * contract_data.wage
				for x in self.medical_ids:
					tahun_param.append(str(x.tahun))

				if str(end_year_formatted.year) not in tahun_param:
					vals = {
						'medical_id' : self.id,
						'saldo_medical' : saldo,
						'tgl_expired'   : end_year_formatted,
						'tahun'			: end_year_formatted.year,
					}
					medical_obj.create(vals)
		else:
			self.medical_trigger = False

	@api.one
	@api.depends('join_date_trigger')
	def _get_join_date(self):
		contract_id = self.env['hr.contract'].search([('employee_id','=',self.id),('state','=','open')])
		if len(contract_id) > 1:
			raise Warning('Karyawan harus memiliki lebih dari 1 kontrak yg running')
		for contract in contract_id:
			if contract.trial_date_start:
				self.join_date = contract.trial_date_start
			else:
				self.join_date = contract.date_start





	medical_ids				= fields.One2many('hr.employee.plafon.medical','medical_id',' ')
	medical_trigger			= fields.Boolean('Med.Trigger', compute="_get_trigger")
	join_date       		= fields.Date('Join Date', compute='_get_join_date',store=True)
	join_date_trigger		= fields.Boolean('JD Trigger') 



	



class hr_employee_plafon_medical(models.Model):
	_name = 'hr.employee.plafon.medical'
	_description = "Plafon Medical"


	medical_id 			= fields.Many2one('hr.employee','Medical')
	saldo_medical		= fields.Float('Saldo Medical')
	tgl_expired			= fields.Date('Tanggal Expired')
	tahun 				= fields.Char('Tahun')


