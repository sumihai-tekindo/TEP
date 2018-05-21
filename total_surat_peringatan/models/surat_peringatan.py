
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, except_orm, Warning, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta




class SuratPeringatan(models.Model):
	_name 	= 'surat.peringatan'
	_rec_name = 'name'


	name 						= fields.Char('Name', required=True, default="/")
	tanggal_pelanggaran			= fields.Date('Tanggal Pelanggaran')
	employee_id 				= fields.Many2one('hr.employee','Karyawan', required=True)
	nama_atasan					= fields.Many2one('hr.employee','Atasan')
	jabatan 					= fields.Many2one('hr.job','Jabatan')
	project_id					= fields.Char('Project')
	start_date					= fields.Date('Start Date', required=True)
	end_date					= fields.Date('End Date', required=True)
	tipe_sp						= fields.Selection([('satu','1'),
													('dua','2'),
													('tiga','3')],'Tipe SP', required=True)
	category_id 				= fields.Many2one('surat.peringatan.category','Category')
	note 						= fields.Text('Note')
	phk							= fields.Boolean('PHK',default=False)
	state 						= fields.Selection([('new','New'),
													('submit_to_legal','Submit to Legal'),
													('submit_to_hrd','Submit to HRD'),
													('approved','Approved'),
													('rejected','Rejected'),
													('done','Done')],'State', default="new")


	@api.onchange('employee_id')
	def onchange_employee(self):
		self.nama_atasan = self.employee_id.parent_id.id
		self.jabatan 	= self.employee_id.job_id.id



	@api.one
	def submit_to_legal(self):
		sp_obj = self.env['surat.peringatan']
		for x in sp_obj.search([('employee_id','=',self.employee_id.id),('id','!=',self.id)]):
			if x.end_date >= self.start_date and x.state == 'approved':
				if x.tipe_sp != 'tiga':
					if x.tipe_sp == self.tipe_sp:
						raise Warning('Karyawan ybs sedang dalam proses SP, harap diperhatikan tipe SP')
					elif x.tipe_sp == 'dua' and self.tipe_sp in ['satu','dua']:
						raise Warning('SP baru harus lebih tinggi')
					else:
						self.state = 'submit_to_legal'
				else:
					self.phk = True
					self.state = 'submit_to_legal'
			else:
				print "aaaa"
		self.state = 'submit_to_legal'


	@api.one
	def submit_to_hrd(self):
		self.state = 'submit_to_hrd'

	@api.multi
	def approve(self):
		if self.phk == True:
			return {
					'type': 'ir.actions.act_window',
					'res_model': 'wizard.phk',
					'view_mode': 'form',
					'view_type': 'form',
					'views': [(False, 'form')],
					'target': 'new',
				}
			self.state = 'approved'
		else:
			self.state = 'approved'



class SuratPeringatanCateg(models.Model):
	_name 	= 'surat.peringatan.category'
	_rec_name = 'name'


	name 			= fields.Char('Name')


class WizardPHK(models.Model):
	_name 	= 'wizard.phk'

	check 		= fields.Char('Check')

	@api.multi
	def yes(self,context):
		data = context.get('active_id',False)
		sp_obj = self.env['surat.peringatan'].search([('id','=',data)])
		employee_obj = self.env['hr.employee'].search([('id','=',sp_obj.employee_id.id)])
		employee_obj.toggle_active()
		sp_obj.state = 'approved'
