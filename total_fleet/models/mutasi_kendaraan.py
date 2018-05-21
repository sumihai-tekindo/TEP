
from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta




class MutasiKendaraan(models.Model):
	_name 	= 'mutasi.kendaraan'
	_rec_name = 'name'



	name 				= fields.Char('Name')


	date 				= fields.Date('Tanggal', default=fields.Date.today())
	fleet_id			= fields.Many2one('fleet.vehicle','Kendaraan')
	nama_karyawan		= fields.Many2one('hr.employee','Karyawan')
	project_id			= fields.Many2one('project.project','Proyek')
	jabatan				= fields.Many2one('hr.job','Jabatan')
	keterangan			= fields.Text('Keterangan')
	state				= fields.Selection([('new','New'),
											('submit','Submit'),
											('approved','Approved'),
											('rejected','Rejected')],'State', default="new")




	@api.onchange('nama_karyawan')
	def onchange_karyawan(self):
		self.jabatan = self.nama_karyawan.job_id


	@api.one
	def submit(self):
		self.state = 'submit'


	@api.one
	def approve(self):
		fleet_obj = self.env['fleet.vehicle'].search([('id','=',self.fleet_id.id)])
		fleet_obj.write({'employee_id' : self.nama_karyawan.id})
		self.state = 'approved'
