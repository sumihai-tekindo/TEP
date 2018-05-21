
from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta




class PinjamanKaryawan(models.Model):
	_name 	= 'pinjaman.karyawan'
	_rec_name = 'name'


	name 				= fields.Char('Name', required=True)
	tanggal 			= fields.Date('Tanggal', default=fields.Date.today(), required=True)
	karyawan_id 		= fields.Many2one('hr.employee','Karyawan', required=True)
	jabatan_id 			= fields.Many2one('hr.job','Jabatan', required=True)
	project_id 			= fields.Many2one('project.project','Project', required=True)
	nilai_pinjaman		= fields.Float('Nilai Pinjaman', required=True)
	jumlah_cicilan 		= fields.Integer('Jumlah Cicilan', required=True)
	cicilan_perbulan 	= fields.Float('Cicilan Perbulan', required=True)
	bulan_awal_pemotongan = fields.Date('Bulan Awal Pemotongan',default=fields.Date.today(), required=True)
	keperluan 			= fields.Char('Keperluan', required=True)
	transfer_ke_rek 	= fields.Many2one('res.bank', 'Transfer ke', required=True)
	no_rekening 		= fields.Char('Nomor Rekening', required=True)
	alasan_reject 		= fields.Text('Alasan Reject', required=True)
	detail_ids 			= fields.One2many('pinjaman.karyawan.detail','detail_id',' ')
	state				= fields.Selection([('new','New'),
											('to_submit','To Submit'),
											('reported','Reported'),
											('posted','Posted'),
											('dalam_cicilan','Dalam Cicilan'),
											('lunas','Lunas'),
											('rejected','Rejected')],'State', default="new")



	@api.one
	def to_submit(self):
		if self.jumlah_cicilan > 10:
			raise Warning('Jumlah cicilan maksimal 10')
		for x in self.detail_ids:
			x.state = 'belum_dibayar'
		self.state = 'to_submit'

	@api.one
	def reported(self):
		self.state = 'reported'

	@api.one
	def posted(self):
		self.state = 'posted'

	@api.one
	def dalam_cicilan(self):
		self.state = 'dalam_cicilan'

	@api.one
	def lunas(self):
		self.state = 'lunas'

	@api.one
	def rejected(self):
		self.state = 'rejected'

	@api.one
	def reset_to_new(self):
		for x in self.detail_ids:
			x.state = 'new'
		self.state = 'new'



	@api.onchange('karyawan_id')
	def onchange_karyawan(self):
		self.jabatan_id = self.karyawan_id.job_id.id

	@api.onchange('jumlah_cicilan','nilai_pinjaman','bulan_awal_pemotongan')
	def onchange_jumlah_cicilan(self):
		v_penambahan_hari = 0
		tot_nilai_cicilan = 0
		tot_sisa_pinjaman = 0
		detail_lines = [(5,0,0)]
		detail_obj = self.env['pinjaman.karyawan.detail']
		if self.jumlah_cicilan > 0 and self.nilai_pinjaman > 0:
			self.cicilan_perbulan = self.nilai_pinjaman / self.jumlah_cicilan
		for x in range(0,self.jumlah_cicilan):
			v_penambahan_hari += 31
			tot_nilai_cicilan += self.cicilan_perbulan
			bulan_awal_pemotongan_formatted = datetime.strptime(self.bulan_awal_pemotongan,'%Y-%m-%d')+ timedelta(days=v_penambahan_hari)
			vals = {
				'detail_id'	: self.id,
				'tanggal_cicil' : bulan_awal_pemotongan_formatted,
				'nilai_cicilan' : self.cicilan_perbulan,
				'total_nilai_cicilan' : tot_nilai_cicilan,
				'sisa_pinjaman' : self.nilai_pinjaman - tot_nilai_cicilan,
			}
			detail_lines.append((0,0,vals))
		self.detail_ids = detail_lines

			

class PinjamanKaryawanDetail(models.Model):
	_name 	= 'pinjaman.karyawan.detail'

	detail_id 			= fields.Many2one('pinjaman.karyawan',' ')
	tanggal_cicil 		= fields.Date('Tanggal Cicil')
	nilai_cicilan 		= fields.Float('Nilai Cicilan')
	total_nilai_cicilan = fields.Float('Total Nilai Cicilan')
	sisa_pinjaman 		= fields.Float('Sisa Pinjaman')
	state 				= fields.Selection([('new','New'),
											('belum_dibayar','Belum dibayar'),
											('lunas','Lunas')],'Status', default="new", readonly=True)