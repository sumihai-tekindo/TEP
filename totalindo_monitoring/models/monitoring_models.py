# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.totalindo_report import terbilang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import odoo.addons.decimal_precision as dp


INDONESIAN_MONTHES = {
	1: 'Januari',
	2: 'Februari',
	3: 'Maret',
	4: 'April',
	5: 'Mei',
	6: 'Juni',
	7: 'Juli',
	8: 'Agustus',
	9: 'September',
	10: 'Oktober',
	11: 'Nopember',
	12: 'Desember',    
}

class monitoring_progress(models.Model):
	_name = 'monitoring.progress'

	@api.depends('detail_line.total_invoice')
	def _amount_all(self):
		for order in self:
			total_amount = 0.0
			for line in order.detail_line:
				total_amount += line.total_invoice
		self.total_amount = total_amount

	contract_id = fields.Many2one('sale.order', string='Contract No', required=True)
	name = fields.Char(string="Reference", default='/', readonly=True)
	partner_id = fields.Many2one('res.partner', string='Customer Name', track_visibility='onchange')
	partner_invoice_id = fields.Many2one('res.partner', string='Customer Address', track_visibility='onchange')
	project_name_id = fields.Many2one('project.project', string='Project Name', track_visibility='onchange')
	revenue_date = fields.Date(string='Revenue Date', required=True)
	currency_id = fields.Many2one("res.currency", readonly=True)
	tp_aktual = fields.Float(string='Total Progress Aktual (%)')
	ap_aktual = fields.Float(string='Akumulasi Progress Aktual (%)')
	tp_approved = fields.Float(string='Total Progress Approved (%)', related='detail_line.pp_approved', store=True)
	ap_approved = fields.Float(string='Akumulasi Progress Approved (%)')
	detail_line = fields.One2many('monitoring.detail','monitoring_progress_id')
	description = fields.Text(string='Description')
	progress_line = fields.One2many('account.invoice', 'progress_id')
	state = fields.Selection([
		('new', 'New'),
		('recognize', 'Recognize Revenue'),
		('approved', 'Customer Approved'),
		('billing', 'Billing'),
		], string='Status', readonly=True, copy=False, default='new', track_visibility='onchange')
	note = fields.Text(string="Description")
	total_amount = fields.Float(string="Total", store=True, readonly=True, compute='_amount_all', track_visibility='always')
	recognize_move_id = fields.Many2one('account.move',"Move Entry Recognize")
	billing_invoice_id = fields.Many2one('account.invoice',"Invoice for Billing")

	@api.onchange('contract_id')
	def monitoring_contract(self):
		self.partner_id = self.contract_id.partner_id.id
		self.partner_invoice_id = self.contract_id.partner_invoice_id.id
		self.project_name_id = self.contract_id.contract_id.id
		self.currency_id = self.contract_id.currency_id.id

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('contract.monitoring') or '/'
			code = self.env['project.project'].browse(vals['project_name_id']).code
			vals['name'] = vals['name'][:10]+'/TEP-'+code+vals['name'][10:]
		return super(monitoring_progress, self).create(vals)

	@api.multi
	def generate_progress(self):
		self.write({'state': 'new'})
		for monitoring in self:
			project_id = monitoring.project_name_id and monitoring.project_name_id.id or False
			project_start_date = monitoring.project_name_id.date_from
			if not project_start_date:
				raise ValidationError(_('You cannot generate progress due to start date in project is undefined!'))
			dt_project_start_date = datetime.strptime(project_start_date,'%Y-%m-%d')
			dt_revenue_date = datetime.strptime(monitoring.revenue_date,'%Y-%m-%d')
			dt_delta_date = dt_revenue_date-dt_project_start_date
			monitoring_id =monitoring.id or False
			if project_id:
				if monitoring.detail_line:
					monitoring.detail_line.unlink()

				task_ids = self.env['project.task'].search([('project_id','=',project_id)])
				header_total_percentage = 0.0
				for task in task_ids:
					t_temp = {
						'monitoring_progress_id': monitoring_id,
						'no_task': task.name or '/',
						'task_id': task.id,
						# 'work_description': task.progress_ids.name,
						'unit_price': task.amount,
						'progress_date': dt_delta_date.days,
						'pp_aktual': task.progress_actual,
						'pp_approved': False,
						'total_revenue': task.progress_actual/100.0 * task.amount,
						'total_invoice': 0.0,
						}
					x = self.env['monitoring.detail'].new(t_temp)

					for progress in task.progress_ids:
						t_temp.update(dict(x._convert_to_write(x._cache),work_description=progress.name))
						self.env['monitoring.detail'].create(t_temp)
					header_total_percentage+=task.progress_actual
				monitoring.tp_aktual = header_total_percentage

	@api.multi
	def recalculate_progress(self):
		self.write({'state': 'recognize'})
		for monitoring in self:
			project_id = monitoring.project_name_id and monitoring.project_name_id.id or False
			project_start_date = monitoring.project_name_id.date_from
			if not project_start_date:
				raise ValidationError(_('You cannot generate progress due to start date in project is undefined!'))
			dt_project_start_date = datetime.strptime(project_start_date,'%Y-%m-%d')
			dt_revenue_date = datetime.strptime(monitoring.revenue_date,'%Y-%m-%d')
			dt_delta_date = dt_revenue_date-dt_project_start_date
			detail_id = monitoring.id
			header_total_percentage = 0.0
			for line in monitoring.detail_line:
				task = line.task_id
				t_temp = {
						'monitoring_progress_id': detail_id,
						'no_task': task.name or '/',
						'task_id': task.id,
						'work_description': task.progress_ids.name,
						'unit_price': task.amount,
						'progress_date': dt_delta_date.days,
						'pp_aktual': task.progress_actual,
						'pp_approved': False,
						'total_revenue': task.progress_actual/100.0 * task.amount,
						'total_invoice': 0.0,
						}
				line.write(t_temp)
				header_total_percentage+=task.progress_actual
			monitoring.tp_aktual = header_total_percentage
			
	@api.multi
	def recognize_revenue(self):
		template_journal = self.env['journal.project'].search([('id','>',0)],limit=1)
		if template_journal:
			for recognize in self:
				try:
					journal_id = template_journal.journal_id.id or False,
				except:
					journal_id = self.env['account.journal'].search([('type','=','sale')],limit=1)
				
				move = {
					'journal_id'	: journal_id,
					'date'			: fields.date.today(),
					'ref'			: recognize.name,
					'line_ids' 		: [],
				}
				amount_progress = (recognize.tp_aktual/100.0)*(recognize.contract_id and recognize.contract_id.amount_total or 0.0)
				tax = template_journal.pph_4_2.compute_all(amount_progress, self.contract_id.company_id.currency_id, 1, False, recognize.partner_id)
				tax_amount =tax['taxes'][0]['amount']
				tax_account =tax['taxes'][0]['account_id']
				tax_name =tax['taxes'][0]['account_id']
				line_revenue = {
					'account_id': template_journal.revenue and template_journal.revenue.id or False,
					'partner_id': recognize.partner_id and recognize.partner_id.id or False,
					'name'		: recognize.name,
					'analytic_account_id': recognize.project_name_id and recognize.project_name_id.analytic_account_id and recognize.project_name_id.analytic_account_id.id or False,
					'debit'		: 0.0,
					'credit'	: amount_progress,
					}
				line_tax = {
					'account_id': template_journal.beban_pajak and template_journal.beban_pajak.id or tax_account or False,
					'partner_id': False,
					'name'		: tax_name,
					'analytic_account_id': False,
					'debit'		: tax_amount,
					'credit'	: False,
					}
				line_ar = {
					'account_id': template_journal.piutang_bruto and template_journal.piutang_bruto.id or False,
					'partner_id': recognize.partner_id and recognize.partner_id.id or False,
					'name'		: recognize.name,
					'analytic_account_id':False,
					'debit'		: amount_progress-tax_amount,
					'credit'	:False,
					'date_due'  :False #isi due date jika perlu
					}
				move.update({
					'line_ids':[(0,0,line_ar),(0,0,line_tax),(0,0,line_revenue)]
					})
				move_id = self.env['account.move'].create(move)
				print "============",move_id
				recognize.write({'recognize_move_id':move_id.id})
				move_id.post()
		self.write({'state': 'approved'})

	@api.multi
	def customer_approved(self):
		self.write({'state': 'billing'})

	@api.multi
	def generate_billing(self, progress):
		gen_invoice = self.env['account.invoice'].search([('id','>',0)],limit=1)

		billing = gen_invoice.create({
			'partner_id': False,
			'partner_shipping_id': False,
			'progress_id': False,
			'no_contract': False,
			'project_name_id': False,
			'invoice_line_ids': [(0, 0, {
				'no_invoice': False,
				'work_description': False,
				'progress_date': False,
				'progress_aktual': False,
				'progress_approved': False,
				'price_unit': False,
				'invoice_line_tax_ids': False,
			})],
			'tanggal_invoice': False,
			'nilai_tender': False,
			'uang_muka': False,
			'retensi': False,
			'currency_id': False,
			'payment_term_id': False,
		})
		invoice.compute_taxes()
		return billing
		self.write({'state': 'recognize'})

class monitoring_detail(models.Model):
	_name = 'monitoring.detail'
	_rec_name = 'no_task'

	monitoring_progress_id = fields.Many2one('monitoring.progress','Detail')
	no_task = fields.Char(string='No. Task')
	task_id = fields.Many2one('project.task',"Related Task")
	task_description = fields.Char(string='Task Name')
	unit_price = fields.Integer(string='Unit Price')
	progress_date = fields.Integer(string='Progress to Date')
	pp_aktual = fields.Float(string='% Progress Aktual')
	pp_approved = fields.Float(string='% Progress Approved')
	total_revenue = fields.Integer(string='Total Revenue')
	total_invoice = fields.Integer(string='Total Invoice', compute="_compute_invoice")
	state = fields.Selection(related='monitoring_progress_id.state', store=True, default='new')

	@api.depends('total_invoice','unit_price', 'pp_approved')
	def _compute_invoice(self):
		for record in self:
			if record.unit_price != 0 and record.pp_approved != 0:
				record.total_invoice = record.unit_price * record.pp_approved/100
