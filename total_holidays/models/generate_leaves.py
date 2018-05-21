from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from datetime import datetime

class GenerateLeaves(models.Model):
    _name = 'generate.leaves'


    name 				= fields.Char('Nama')
    tahun 				= fields.Char('Tahun')



    @api.one
    def generate(self):
        datetimeFormat = '%Y-%m-%d'
        holidays_obj = self.env['hr.holidays']
        ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
        end_year_formatted = datetime.strptime(str(ending_day_of_current_year),datetimeFormat)
        prof_data_permanen = self.env['hr.employee.category'].search([('name','=','Permanen')])
        prof_data_kontrak = self.env['hr.employee.category'].search([('name','=','Kontrak')])
        permanen_emp = self.env['hr.employee'].search([('id','!=',0)])
        jenis_cuti	= self.env['hr.holidays.status'].search([('name','=','Cuti Tahunan')])
        jenis_cuti_pernikahan	= self.env['hr.holidays.status'].search([('name','=','Cuti Pernikahan')])
        for emp in permanen_emp:
            if prof_data_permanen in emp.category_ids:
            	join_date_formatted = datetime.strptime(emp.join_date, datetimeFormat)
            	duration = str((end_year_formatted-join_date_formatted).days)
            	vals = {
            		'name' : "Legal Leaves" + emp.name + self.tahun,
            		'holiday_status_id' : jenis_cuti.id,
            		'number_of_days_temp': int(duration) / 30,
            		'mode'				: 'employee',
            		'employee_id'		: emp.id,
            		'department_id'		: emp.department_id.id,
            		'type'				: 'add',
            	}
            	holidays_obj.create(vals)
            	if emp.gender == 'female' and emp.marital == 'married':
            		jenis_cuti_hamil = self.env['hr.holidays.status'].search([('name','=','Cuti Hamil')])
            		vals_hamil = {
            			'name' : "Cuti Hamil" + emp.name + self.tahun,
	            		'holiday_status_id' : jenis_cuti_hamil.id,
	            		'number_of_days_temp': 3,
	            		'mode'				: 'employee',
	            		'employee_id'		: emp.id,
	            		'department_id'		: emp.department_id.id,
	            		'type'				: 'add',
            		}
            		holidays_obj.create(vals_hamil)

            	vals_pernikahan = {
            		'name' : "Cuti Pernikahan" + emp.name + self.tahun,
            		'holiday_status_id' : jenis_cuti_pernikahan.id,
            		'number_of_days_temp': 3,
            		'mode'				: 'employee',
            		'employee_id'		: emp.id,
            		'department_id'		: emp.department_id.id,
            		'type'				: 'add',
            	}
            	holidays_obj.create(vals_pernikahan)
