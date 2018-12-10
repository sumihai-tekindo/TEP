
from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta


class MutasiKaryawan(models.Model):
	_name 	= 'hr.mutasi.karyawan'
	_rec_name = 'name'


	name 						= fields.Char('Name')
	tanggal_pengajuan 			= fields.Date('Tanggal Pengajuan', default=fields.Date.today())
	kebutuhan_proyek			= fields.Many2one('project.project','Kebutuhan Proyek')
	state 						= fields.Selection([('new','New'),
													('submit','Submit'),
													('approved','Approved'),
													('rejected','Rejected')],'State', default="new")

	note 						= fields.Text('Note')
	detail_ids 					= fields.One2many('hr.mutasi.karyawan.detail','detail_id','Detail')




	@api.one
	def submit(self):
		self.state = 'submit'

	@api.one
	def approve(self):
		for detail in self.detail_ids:
			lead_id.write({'project': detail.proyek_dituju.id,'job_id':detail.jabatan_baru})
		self.state = 'approved'

	@api.one
	def reject(self):
		self.state = 'reject'


class MutasiKaryawanDetail(models.Model):
	_name 	= 'hr.mutasi.karyawan.detail'

	detail_id 					= fields.Many2one('hr.mutasi.karyawan',' ')
	nama_karyawan				= fields.Many2one('hr.employee','Nama Karyawan')
	proyek_semula				= fields.Many2one('project.project','Proyek Semula')
	jabatan_semula				= fields.Many2one('hr.job','Jabatan Semula')
	proyek_dituju				= fields.Many2one('project.project','Proyek Dituju')
	jabatan_baru				= fields.Many2one('hr.job','Jabatan Baru')
	mobilisasi_date				= fields.Date('Mobilisasi')

	@api.onchange('nama_karyawan')
	def onchange_nama_karyawan(self):
		self.proyek_semula = self.nama_karyawan.project.detail_id
		self.jabatan_semula = self.nama_karyawan.job_id.id