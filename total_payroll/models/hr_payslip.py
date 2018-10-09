from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime
from odoo.exceptions import UserError





class hr_payslip(models.Model):
	_inherit = 'hr.payslip'



	@api.multi
	def action_payslip_done(self):
		dateFormat = '%Y-%m-%d'
		today = fields.Date.today()
		bulan_gajian = datetime.strptime(self.date_from,dateFormat).month
		tahun_gajian = datetime.strptime(self.date_from,dateFormat).year
		for cicilan in self.contract_id.pinjaman_id.detail_ids:
			bulan_pemotongan = datetime.strptime(cicilan.tanggal_cicil,dateFormat).month
			tahun_pemotongan = datetime.strptime(cicilan.tanggal_cicil,dateFormat).year
			if bulan_gajian == bulan_pemotongan and tahun_gajian == tahun_pemotongan:
				cicilan.write({'state': 'lunas'})
		self.compute_sheet()
		return self.write({'state': 'done'})