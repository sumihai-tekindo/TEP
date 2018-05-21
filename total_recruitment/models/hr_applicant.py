from odoo import models, fields, api, _


class hr_applicant(models.Model):
	_inherit = 'hr.applicant'



	nomor_npwp 				= fields.Char('No.NPWP')
	no_ktp 					= fields.Char('No.KTP')
	keluarga_ids 			= fields.One2many('hr.applicant.keluarga','keluarga_id',' ')
	pendidikan_ids 			= fields.One2many('hr.applicant.pendidikan.terakhir','pendidikan_id',' ')
	riwayat_pekerjaan_ids	= fields.One2many('hr.applicant.riwayat.pekerjaan','riwayat_pekerjaan_id',' ')



	@api.multi
	def create_employee_from_applicant(self):
		""" Create an hr.employee from the hr.applicants """
		employee = False
		for applicant in self:
			address_id = contact_name = False
			if applicant.partner_id:
				address_id = applicant.partner_id.address_get(['contact'])['contact']
				contact_name = applicant.partner_id.name_get()[0][1]
			if applicant.job_id and (applicant.partner_name or contact_name):
				applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
				employee = self.env['hr.employee'].create({'name': applicant.partner_name or contact_name,
									'job_id': applicant.job_id.id,
									'address_home_id': address_id,
									'department_id': applicant.department_id.id or False,
									'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
									'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
									'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False})
				for keluarga in applicant.keluarga_ids:
					keluarga_det = self.env['hr.employee.keluarga']
					vals = {
						'keluarga_id' : employee.id,
						'nama'		: keluarga.nama,
						'hubungan'	: keluarga.hubungan,
						'tgl_lahir' : keluarga.tgl_lahir,
					}
					keluarga_det.create(vals)
				for pendidikan in applicant.pendidikan_ids:
					pendidikan_det = self.env['hr.employee.pendidikan.terakhir']
					vals = {
							'pendidikan_id' : employee.id,
							'tahun'			: pendidikan.tahun,
							'gelar'			: pendidikan.gelar,
							'jurusan'		: pendidikan.jurusan,
							'nama_sekolah'	: pendidikan.nama_sekolah
							}
					pendidikan_det.create(vals)
				for riwayat in applicant.riwayat_pekerjaan_ids:
					riwayat_det 	= self.env['hr.employee.riwayat.pekerjaan']
					vals = {
						'riwayat_pekerjaan_id' : employee.id,
						'tahun'					: riwayat.tahun,
						'jabatan'				: riwayat.jabatan,
						'perusahaan'			: riwayat.perusahaan
					}
					riwayat_det.create(vals)

				applicant.write({'emp_id': employee.id})
				applicant.job_id.message_post(
					body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
					subtype="hr_recruitment.mt_job_applicant_hired")
				employee._broadcast_welcome()
			else:
				raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

		employee_action = self.env.ref('hr.open_view_employee_list')
		dict_act_window = employee_action.read([])[0]
		if employee:
			dict_act_window['res_id'] = employee.id
		dict_act_window['view_mode'] = 'form,tree'
		return dict_act_window










class hr_applicant_keluarga(models.Model):
	_name = 'hr.applicant.keluarga'
	_description = "Keluarga"



	keluarga_id 			= fields.Many2one('hr.applicant',' ')
	nama 					= fields.Char('Nama')
	hubungan 				= fields.Char('Hubungan')
	tgl_lahir 				= fields.Date('Tanggal Lahir')



class hr_applicant_pendidikan(models.Model):
	_name  			= 'hr.applicant.pendidikan.terakhir'
	_description	= 'Pendidikan Terakhir'


	pendidikan_id 			= fields.Many2one('hr.applicant',' ')
	tahun 					= fields.Char('Tahun')
	gelar					= fields.Char('Gelar')
	jurusan 				= fields.Char('Jurusan')
	nama_sekolah			= fields.Char('Nama Sekolah / Universitas')


class hr_applicant_riawayat_pekerjaan(models.Model):
	_name  			= 'hr.applicant.riwayat.pekerjaan'
	_description	= 'Riwayat Pekerjaan'


	riwayat_pekerjaan_id 			= fields.Many2one('hr.applicant',' ')
	tahun 							= fields.Char('Tahun')
	jabatan 						= fields.Char('Jabatan')
	perusahaan						= fields.Char('Perusahaan')


