from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime
from odoo.exceptions import UserError


class hr_contract(models.Model):
	_inherit = 'hr.contract'

	transport_wage 		= fields.Float('Transport', required=True)
	meal_wage			= fields.Float('Meal',required=True)
	overtime_wage		= fields.Float('Overtime',required=True)

	cicilan_active		= fields.Float('Cicilan',compute='_get_cicilan')

	is_sakit_berkepanjangan = fields.Boolean('Sakit Berkepanjangan?', compute='_is_sakit_berkepanjangan')

	medical_reimbursement = fields.Float('Medical Reimbursement', compute='_get_medical_reimbursement')

	cuti_minus			= fields.Float('Cuti Minus',compute='_get_cuti_minus')

	cuti_sakit_lebih_dari_satu_hari = fields.Float('Cuti Sakit Lebih dari 1 Hari tanpa Surat Dokter',compute='_get_cuti_sakit')
	pinjaman_id 		= fields.Many2one('pinjaman.karyawan','Pinjaman',compute='_get_cicilan')
	#cuti_sakit_lebih_dari_satu_hari = fields.Float('Cuti Minus')

	@api.onchange('trial_date_start','date_start')
	def onchange_date_start(self):
		employee_obj = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
		if self.employee_id.join_date_trigger == True:
			employee_obj.write({'join_date_trigger':False})
		else:
			employee_obj.write({'join_date_trigger':True})


	@api.one
	def _get_cicilan(self):
		datetimeFormat = '%Y-%m-%d'
		today = fields.Date.today()
		bulan_berjalan = datetime.strptime(today,datetimeFormat).month
		if self.state == 'open':
			pinjaman_ids = self.env['pinjaman.karyawan'].search([('karyawan_id','=',self.employee_id.id),('state','=','posted')])
			for pinjaman in pinjaman_ids:
				for detail in pinjaman.detail_ids:
					if detail.state == 'belum_dibayar':
						bulan_pemotongan = datetime.strptime(detail.tanggal_cicil,datetimeFormat).month
						if bulan_pemotongan == bulan_berjalan:
							self.cicilan_active = detail.nilai_cicilan
							self.pinjaman_id = pinjaman.id

	@api.one
	def _get_medical_reimbursement(self):
		datetimeFormat = '%Y-%m-%d'
		today = fields.Date.today()
		bulan_berjalan = datetime.strptime(today,datetimeFormat).month
		if self.state == 'open':
			expense_sheet_ids = self.env['hr.expense.sheet'].search([('employee_id','=',self.employee_id.id),('state','=','post')])
			for expense in expense_sheet_ids:
				bulan_pemotongan = datetime.strptime(expense.accounting_date,datetimeFormat).month
				if bulan_pemotongan == bulan_berjalan:
					self.medical_reimbursement += expense.total_amount

	@api.one
	def _get_cuti_minus(self):
		datetimeFormat = '%Y-%m-%d'
		today = fields.Date.today()
		bulan_berjalan = datetime.strptime(today,datetimeFormat).month
		if self.state == 'open':
			jatah_cuti = self.env['hr.holidays.remaining.leaves.user'].search([('name','=',self.employee_id.name)])
			for all_jatah in jatah_cuti:
				if all_jatah.no_of_leaves < 0:
					self.cuti_minus += all_jatah.no_of_leaves


	@api.one
	def _get_cuti_sakit(self):
		datetimeFormat = '%Y-%m-%d %H:%M:%S'
		dateFormat = '%Y-%m-%d'
		today = fields.Date.today()
		bulan_berjalan = datetime.strptime(today,dateFormat).month
		if self.state == 'open':
			cuti_sakit = self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('type','=','remove'),('state','=','validate')])
			for sakit in cuti_sakit:
				bulan_cuti = datetime.strptime(sakit.date_from,datetimeFormat).month
				if bulan_cuti == bulan_berjalan:
					if sakit.number_of_days_temp > 1 and not sakit.surat_keterangan_dokter:
						self.cuti_sakit_lebih_dari_satu_hari = sakit.number_of_days_temp - 1



	def _is_sakit_berkepanjangan(self):
		datetimeFormat = '%Y-%m-%d %H:%M:%S'
		dateFormat = '%Y-%m-%d'
		today = fields.Date.today()
		bulan_berjalan = datetime.strptime(today,dateFormat).month
		if self.state == 'open':
			sakit_berkepanjangan_ids = self.env['hr.sakit.berkepanjangan'].search([('employee_id','=',self.employee_id.id),('state','=','progress')])
			if sakit_berkepanjangan_ids:
				self.is_sakit_berkepanjangan = True
			else:
				self.is_sakit_berkepanjangan = False
			# for sakit_berkepanjangan in sakit_berkepanjangan_ids:
			# 	bulan_awal_sakit = datetime.strptime(sakit_berkepanjangan.date_start,datetimeFormat).month
			# 	lama_sakit = bulan_berjalan - bulan_awal_sakit:


	def get_sakit_berkepanjangan(self,is_sakit_berkepanjangan,employee_id,contract_id,basic,allowance,deduction):
		datetimeFormat = '%Y-%m-%d'
		dateFormat = '%Y-%m-%d'
		today = fields.Date.today()
		bulan_berjalan = datetime.strptime(today,dateFormat)
		if is_sakit_berkepanjangan == True:
			sakit_berkepanjangan_ids = self.env['hr.sakit.berkepanjangan'].search([('employee_id','=',employee_id),('state','=','progress')])
			if len(sakit_berkepanjangan_ids) == 1:
				for x in sakit_berkepanjangan_ids:
					bulan_awal_sakit = datetime.strptime(x.date_start,datetimeFormat)
					lama_sakit_str = str((bulan_berjalan-bulan_awal_sakit).days)
					lama_sakit = int(lama_sakit_str) / 30
					contract_ids = self.env['hr.contract'].search([('id','=',contract_id)])
					if len(contract_ids) == 1:
						for con in contract_ids:
							if lama_sakit > 0 and lama_sakit <= 4:
								result = con.wage + con.transport_wage + con.meal_wage + con.overtime_wage
							elif lama_sakit > 4 and lama_sakit <=8:
								result = ((con.wage + con.transport_wage + con.meal_wage + con.overtime_wage) * 75)/100
							elif lama_sakit > 8 and lama_sakit <= 12:
								result = ((con.wage + con.transport_wage + con.meal_wage + con.overtime_wage) * 50)/100
							elif lama_sakit > 12 and lama_sakit <= 16:
								result = ((con.wage + con.transport_wage + con.meal_wage + con.overtime_wage) * 25)/100
							else:
								result = 0

		else:
			result = int(basic) + int(allowance) + int(deduction)


		return int(result)




	def get_thr(self,payslip_id,contract_id):
		datetimeFormat = '%Y-%m-%d'
		dateFormat = '%Y-%m-%d'
		today = fields.Date.today()
		bulan_berjalan = datetime.strptime(today,dateFormat)
		payslip_ids = self.env['hr.payslip'].search([('id','=',payslip_id)])
		for x in payslip_ids:
			date_to = datetime.strptime(x.date_to,dateFormat).month
			if date_to == 12:
				join_date = datetime.strptime(x.employee_id.join_date,datetimeFormat)
				bulan_payslip = datetime.strptime(x.date_to,datetimeFormat)
				lama_kerja_str = str((bulan_payslip-join_date).days)
				lama_kerja = int(lama_kerja_str) / 30
				contract_ids = self.env['hr.contract'].search([('id','=',contract_id)])
				if len(contract_ids) == 1:
						for con in contract_ids:
							print "kkkkkk"
							if lama_kerja <= 12:
								result = (lama_kerja/12) * (con.wage + con.transport_wage + con.meal_wage + con.overtime_wage)
							else:
								result = con.wage + con.transport_wage + con.meal_wage + con.overtime_wage
			else:
				result = 0

		return int(result)

                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code (previously computed)
                    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
                    # worked_days: object containing the computed worked days
                    # inputs: object containing the computed inputs

                    # Note: returned value have to be set in the variable 'result'

                    #result = rules.NET > categories.NET * 0.10





      