from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime
from odoo.exceptions import UserError


class hr_expense(models.Model):
	_inherit = 'hr.expense'



	tipe_medical			= fields.Many2one('hr.plafon.medical','Tipe Medical')
	nilai_maksimal			= fields.Float('Nilai Maksimal',compute="_get_nilai", store=True)


	nama_pasien 			= fields.Char('Nama Pasien')
	nama_dokter				= fields.Char('Nama Dokter')
	nama_rumah_sakit		= fields.Char('Nama Rumah Sakit')
	nama_klinik				= fields.Char('Nama Klinik')
	nama_lab				= fields.Char('Nama Lab.')
	penyakit_diderita		= fields.Char('Penyakit diderita')
	butuh_istirahat			= fields.Selection([('ya','Ya'),
												('tidak','Tidak')],'Butuh Istirahat ?')

	istirahat_sakit_selama = fields.Integer('Istirahat Sakit Selama')
	istirahat_sakit_selection = fields.Selection([('hari','Hari'),
													('minggu','Minggu'),
													('bulan','Bulan')])
	lain_lain				= fields.Char('Lain-lain')
	biaya_konsultasi_dokter	= fields.Float('Biaya Konsultasi Dokter')
	biaya_obat				= fields.Float('Biaya Obat')
	biaya_lab				= fields.Float('Biaya Lab.')
	biaya_rumah_sakit		= fields.Float('Biaya Rumah Sakit')
	biaya_lain				= fields.Float('Biaya Lain')
	total_biaya				= fields.Float('Total Biaya')
	total_penggantian		= fields.Float('Total Penggantian')

	tahun					= fields.Char('Tahun', compute='_get_tahun', store=True)


	@api.one
	@api.depends('tipe_medical','product_id')
	def _get_nilai(self):
		if self.tipe_medical and self.product_id.name == 'Expenses':
			self.nilai_maksimal = self.tipe_medical.nilai

	state = fields.Selection([
        ('draft', 'To Submit'),
        ('reported', 'Approved by PM'),
        ('done', 'Posted'),
        ('refused', 'Refused')
        ], compute='_compute_state', string='Status', copy=False, index=True, readonly=True, store=True,
        help="Status of the expense.")	


	@api.one
	@api.depends('date')
	def _get_tahun(self):
		get_year = datetime.strptime(self.date, '%Y-%m-%d').year
		self.tahun = get_year

	@api.depends('biaya_konsultasi_dokter','biaya_obat','biaya_lab','biaya_rumah_sakit','biaya_lain','total_biaya')
	def _compute_amount(self):
		for expense in self:
			expense.total_amount = expense.total_penggantian


	@api.onchange('biaya_konsultasi_dokter','biaya_obat','biaya_lab','biaya_rumah_sakit','biaya_lain','total_biaya','tipe_medical')
	def onchange_biaya(self):
		self.total_biaya = self.biaya_konsultasi_dokter + self.biaya_obat + self.biaya_lab + self.biaya_rumah_sakit + self.biaya_lain
		if self.product_id.name == 'Expenses' and self.tipe_medical.name != 'Sakit':
			if self.total_biaya > self.nilai_maksimal:
				self.total_penggantian = self.nilai_maksimal
			else:
				self.total_penggantian = self.total_biaya
		else:
			print "qqqqqqqqq", self.total_biaya
			self.total_penggantian = (self.total_biaya*90)/100

	@api.multi
	def submit_expenses(self):
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
		datetimeFormat = '%Y-%m-%d'
		plafon_amount = []
		prof_data_probation = self.env['hr.employee.category'].search([('name','=','Probation')])
		prof_data_kontrak = self.env['hr.employee.category'].search([('name','=','Kontrak')])
		date_expense = datetime.strptime(self.date, datetimeFormat)
		date_expense_year = date_expense.year
		if self.product_id.name == 'Expenses' and self.tipe_medical.name != 'Sakit':
			if prof_data_probation in self.employee_id.category_ids:
				raise UserError(_("Maaf, karyawan masih probation"))
			if self.employee_id.gender == 'female' and not self.employee_id.surat_pernyataan:
				raise UserError(_('Karyawati harus melampirkan surat pernyataan'))

			for x in self.employee_id.medical_ids:
				plafon_amount.append(str(x.tahun))


			if str(date_expense_year) not in plafon_amount:
				raise UserError(_('Plafon tidak Tersedia'))
			else:
				for x in self.employee_id.medical_ids:
					if str(date_expense_year) == x.tahun:
						if self.total_amount > x.saldo_medical and self.tipe_medical.name == 'Sakit':
							raise UserError(_('Jumlah plafon lebih besar dari plafon yang tersedia'))
		else:
			if prof_data_probation in self.employee_id.category_ids:
				raise UserError(_("Maaf, karyawan masih probation"))
			if self.employee_id.gender == 'female' and not self.employee_id.surat_pernyataan:
				raise UserError(_('Karyawati harus melampirkan surat pernyataan'))

			for x in self.employee_id.medical_ids:
				plafon_amount.append(str(x.tahun))


			if str(date_expense_year) not in plafon_amount:
				raise UserError(_('Plafon tidak Tersedia'))
			else:
				for x in self.employee_id.medical_ids:
					if str(date_expense_year) == x.tahun:
						if self.total_amount > x.saldo_medical and self.tipe_medical.name == 'Sakit':
							raise UserError(_('Jumlah plafon lebih besar dari plafon yang tersedia'))



		if any(expense.state != 'draft' for expense in self):
			raise UserError(_("You cannot report twice the same line!"))
		if len(self.mapped('employee_id')) != 1:
			raise UserError(_("You cannot report expenses for different employees in the same report!"))
		return {
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'hr.expense.sheet',
			'target': 'current',
			'context': {
				'default_expense_line_ids': [line.id for line in self],
				'default_employee_id': self[0].employee_id.id,
				'default_name': self[0].name if len(self.ids) == 1 else ''
			}
		}






class hr_expense_sheet(models.Model):
	_inherit = 'hr.expense.sheet'


	accounting_date			= fields.Date('Accounting Date', default=fields.Date.today())
	state 					= fields.Selection([('submit', 'Submitted'),
						                              ('approve', 'Approved by HRD'),
						                              ('post', 'Posted'),
						                              ('done', 'Paid'),
						                              ('cancel', 'Refused')
						                              ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='submit', required=True,
						        help='Expense Report State')

	@api.multi
	def action_sheet_move_create(self):
		datetimeFormat = '%Y-%m-%d'
		date_expense = datetime.strptime(self.accounting_date, datetimeFormat)
		date_expense_year = date_expense.year

		if any(sheet.state != 'approve' for sheet in self):
			raise UserError(_("You can only generate accounting entry for approved expense(s)."))

		if any(not sheet.journal_id for sheet in self):
			raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

		res = self.mapped('expense_line_ids').action_move_create()

		if not self.accounting_date:
			self.accounting_date = self.account_move_id.date

		if self.payment_mode=='own_account':
			self.write({'state': 'post'})
		else:
			self.write({'state': 'done'})

		for plafon in self.employee_id.medical_ids:
			if str(date_expense_year) == plafon.tahun:
				total = plafon.saldo_medical - self.total_amount
				if total < 0:
					raise Warning('Error')
				else:
					plafon.write({'saldo_medical': total})



		return res