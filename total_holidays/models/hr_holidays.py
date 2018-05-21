from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta


class hr_holidays(models.Model):
	_inherit = 'hr.holidays'



	karyawan_pengganti		= fields.Many2one('hr.employee','Karyawan Pengganti')

	state = fields.Selection([
        ('draft', 'To Submit'),
        ('approve_by_manager','Approve by Manager'),
        ('approve_by_pm','Approve by PM'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
           )


	@api.one
	def approve_by_manager(self):
		self.state = 'approve_by_manager'

	@api.one
	def approve_by_pm(self):
		self.state = 'approve_by_pm'

	@api.one
	def approve_by_hrd(self):
		self.state = 'validate'


	# @api.onchange('date_from')
	# def _onchange_date_from(self):
	# 	number_of_days = 0
	# 	date_from = self.date_from
	# 	date_to = self.date_to
	# 	array_holiday = []
        
	# 	if self.date_from:
	# 		get_leave_year = datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S').year
	# 		query_holiday = self.env['hr.holidays.public'].search([('year', '=', get_leave_year)])

	# 		for key in query_holiday.line_ids:
	# 			array_holiday.append(key.date)

 #            # Compute and update the number of days
	# 		if (date_to and date_from) and (date_from <= date_to):
	# 			self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
	# 		else:
	# 			self.number_of_days_temp = 0
	# 		print "2222222222", self.number_of_days_temp
                
	# 		for x in range(0, int(self.number_of_days_temp)):
	# 			print ">>>>>>", x
	# 			dateLeaveRange = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S') + timedelta(days=x)
	# 			dayLeave = dateLeaveRange.strftime("%A")
	# 			if dayLeave == 'Sunday' or dayLeave == 'Saturday':
	# 				number_of_days += 0
	# 			else:
	# 				if str(dateLeaveRange.date()) in array_holiday:
	# 					number_of_days += 0
	# 				else:
	# 					number_of_days += 1
                    
	# 			self.number_of_days_temp = number_of_days

	@api.onchange('date_to')        
	def _onchange_date_to(self):
		date_from = self.date_from
		print "date_from", date_from
		date_to = self.date_to
		number_of_days = 0
		array_holiday = []
        
		if self.date_from:
			get_leave_year = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S').year
			query_holiday = self.env['hr.holidays.public'].search([('year', '=', get_leave_year)])
			for key in query_holiday.line_ids:
				array_holiday.append(key.date)

			# Compute and update the number of days
			if (date_to and date_from) and (date_from <= date_to):
				self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
			else:
				self.number_of_days_temp = 0
			print "xxx", self.number_of_days_temp
			#print "Total Hari = ", self.number_of_days_temp
			for x in range(0, int(self.number_of_days_temp)):
				print "xx123", x
				dateLeaveRange = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S') + timedelta(days=x)
				print "xxxxxxxxx",dateLeaveRange
				dayLeave = dateLeaveRange.strftime("%A")
			 	print "HARI : ", dayLeave
				if dayLeave == 'Sunday' or dayLeave == 'Saturday':
					number_of_days += 0
				else:
					if str(dateLeaveRange.date()) in array_holiday:
						number_of_days += 0
					else:
						number_of_days += 1
					self.number_of_days_temp = number_of_days