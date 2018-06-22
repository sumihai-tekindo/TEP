from odoo import models, fields, api, _
from datetime import datetime


class hr_employee(models.Model):
	_inherit = 'hr.employee'



	nomor_npwp 				= fields.Char('No.NPWP')
	keluarga_ids 			= fields.One2many('hr.employee.keluarga','keluarga_id','Keluarga')
	pendidikan_ids 			= fields.One2many('hr.employee.pendidikan.terakhir','pendidikan_id','Pendidikan')
	riwayat_pekerjaan_ids	= fields.One2many('hr.employee.riwayat.pekerjaan','riwayat_pekerjaan_id','Riwayat Pekerjaan')
	posisi_terakhir_ids 	= fields.One2many('hr.employee.posisi.terakhir','posisi_terakhir_id','Posisi Terakhir')
	surat_pernyataan 		= fields.Binary('Surat Pernyataan')

	count_pinjaman         = fields.Integer('#Pinjaman', compute='_get_pinjaman')
	count_expense		   = fields.Integer('#Expense', compute='_get_expense')
	count_sp 				= fields.Integer('#Surat Peringatan', compute='_get_sp')
	nik						= fields.Char('NIK', compute='_get_nik', store=True)
	nomor_urut				= fields.Char('No Urut')



	@api.one
	@api.depends('nomor_urut')
	def _get_nik(self):
		datetimeFormat = '%Y-%m-%d'
		stat_number = 0
		join_date_formatted = datetime.strptime(str(self.join_date),datetimeFormat)
		tahun = str(join_date_formatted.year)
		bulan = str('%02d' % join_date_formatted.month)

		prof_data_permanen = self.env['hr.employee.category'].search([('name','=','Permanen')])
		prof_data_kontrak = self.env['hr.employee.category'].search([('name','=','Kontrak')])
		prof_data_evaluasi = self.env['hr.employee.category'].search([('name','=','Evaluasi')])

		if prof_data_permanen in self.category_ids:
			stat_number = 1
		elif prof_data_kontrak in self.category_ids:
			stat_number = 2
		elif prof_data_evaluasi  in self.category_ids:
			stat_number = 0

		self.nik = str(tahun) + str(bulan) + str(stat_number) + str(self.nomor_urut) 


		print "tahun", tahun,bulan





	@api.one
	def _get_pinjaman(self):
		count_pinjaman = self.env['pinjaman.karyawan'].search([('karyawan_id', '=', self.id)])
		self.count_pinjaman = len(count_pinjaman)

	@api.one
	def _get_sp(self):
		count_sp = self.env['surat.peringatan'].search([('employee_id', '=', self.id)])
		self.count_sp = len(count_sp)



	@api.one
	def _get_expense(self):
		count_expense = self.env['hr.expense'].search([('employee_id', '=', self.id),('state','!=','draft')])
		self.count_expense = len(count_expense)



	@api.multi
	def action_view_sp(self):
		self.ensure_one()
		action = self.env.ref('total_surat_peringatan.action_surat_peringatan').read()[0]
		action['context'] = {
		'search_default_employee_id': self.id,
		}
		return action



	@api.multi
	def action_view_pinjaman(self):
		self.ensure_one()
		action = self.env.ref('total_pinjaman_karyawan.action_pinjaman_karyawan').read()[0]
		action['context'] = {
		'search_default_karyawan_id': self.id,
		}
		return action

	@api.multi
	def action_view_expense(self):
		self.ensure_one()
		action = self.env.ref('hr_expense.hr_expense_actions_my_unsubmitted').read()[0]
		action['context'] = {
		'search_default_employee_id': self.id,
		}
		return action





class hr_employee_keluarga(models.Model):
	_name = 'hr.employee.keluarga'
	_description = "Keluarga"



	keluarga_id 			= fields.Many2one('hr.employee',' ')
	nama 					= fields.Char('Nama')
	hubungan 				= fields.Char('Hubungan')
	tgl_lahir 				= fields.Date('Tanggal Lahir')



class hr_employee_pendidikan(models.Model):
	_name  			= 'hr.employee.pendidikan.terakhir'
	_description	= 'Pendidikan Terakhir'


	pendidikan_id 			= fields.Many2one('hr.employee',' ')
	tahun 					= fields.Char('Tahun')
	gelar					= fields.Char('Gelar')
	jurusan 				= fields.Char('Jurusan')
	nama_sekolah			= fields.Char('Nama Sekolah / Universitas')


class hr_employee_riawayat_pekerjaan(models.Model):
	_name  			= 'hr.employee.riwayat.pekerjaan'
	_description	= 'Riwayat Pekerjaan'


	riwayat_pekerjaan_id 			= fields.Many2one('hr.employee',' ')
	tahun 							= fields.Char('Tahun')
	jabatan 						= fields.Char('Jabatan')
	perusahaan						= fields.Char('Perusahaan')


class hr_employee_posisi_terakhir(models.Model):
	_name  			= 'hr.employee.posisi.terakhir'
	_description	= 'Posisi Terakhir'


	posisi_terakhir_id 				= fields.Many2one('hr.employee',' ')
	tahun 							= fields.Char('Tahun')
	gelar 							= fields.Char('Gelar')
	proyek 							= fields.Char('Proyek')


