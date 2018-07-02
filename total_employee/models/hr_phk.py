from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo.tools.safe_eval import safe_eval


class PemutusanHubunganKerja(models.Model):
	_name 	= 'hr.phk'
	_rec_name = 'employee_id'



	employee_id			= fields.Many2one('hr.employee','Nama')
	jabatan_id			= fields.Many2one('hr.job','Jabatan')
	project_id			= fields.Many2one('project.project','Project')
	mulai_bekerja		= fields.Date('Mulai Bekerja')
	tanggal_phk			= fields.Date('Tanggal PHK')
	# #alasan				= fields.Selection([('kedisiplinan','Kedisiplinan'),
	# 										('sakit_berkepanjangan','Sakit Berkepanjangan'),
	# 										('performance','Performance'),
	# 										('tidak_lulus_prob','Tidak Lulus Probation')])

	alasan_id 			= fields.Many2one('hr.phk.alasan','Alasan')

	note				= fields.Text('Note')
	state				= fields.Selection([('new','New'),
											('submit_to_legal','Submit to Legal'),
											('submit_to_hrd','Submit to HRD'),
											('approved','Approved'),
											('rejected','Rejected')],'State', default='new')


	x_value				= fields.Float('X')
	y_value				= fields.Float('Y')
	z_value				= fields.Float('Z')
	o_value				= fields.Float('O')
	code				= fields.Char('Code')

	value_all			= fields.Float('Value All')


	@api.onchange('code')
	def onchange_code(self):
		code = self.code
		#code = compile('a = 1 + 2', '<string>', 'exec')
		x = self.x_value
		y = self.y_value
		z = self.z_value
		o = self.o_value

		# incr = 0

		# # print "222",x,y,z,o
		# # a = safe_eval(self.code,mode='exec')
		# for loop in self.code:
		# 	print "222", loop
		# 	if loop == 'x':
		# 		x_val = x
		# 	elif loop == 'y':
		# 		y_val = y
		# 	elif loop == 'z':
		# 		z_val = z
		# 	elif loop == 'o':
		# 		o_val = o
		# 	incr += 1
		result = eval(self.code)
		self.value_all = result





	@api.onchange('employee_id')
	def onchange_employee(self):
		self.jabatan_id = self.employee_id.job_id.id
		self.mulai_bekerja	= self.employee_id.join_date


	@api.one
	def submit_to_legal(self):
		self.state = 'submit_to_legal'

	@api.one
	def submit_to_hrd(self):
		self.state = 'submit_to_hrd'

	@api.one
	def approved(self):
		employee_obj = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
		employee_obj.toggle_active()
		self.state = 'approved'

	@api.one
	def rejected(self):
		self.state = 'rejected'


class PemutusanHubunganKerjaAlasan(models.Model):
	_name 	= 'hr.phk.alasan'
	_rec_name = 'name'


	name 		= fields.Char('Alasan')