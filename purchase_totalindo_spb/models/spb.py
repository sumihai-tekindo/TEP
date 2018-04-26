from odoo import models, fields, api
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp

class SPB(models.Model):
	
	_name = 'spb'

	name = fields.Char(default="New", string="Nomer SPB")
	tanggal_spb = fields.Date(default=fields.Date.today, string="Tanggal SPB") 
	proyek_id = fields.Many2one('project.project', string="Proyek")
	departemen_id = fields.Many2one('hr.department', string="Departemen")
	budegeted = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Budgeted")
	sifat_kebutuhan = fields.Char(string="Sifat Kebutuhan")
	tanggal_diperlukan = fields.Date(default=fields.Date.today, string="Tanggal Diperlukan")
	# nomer_gambar =
	notes = fields.Text('Terms and Conditions')

	states = fields.Selection([('draft', 'New'),('confirm', 'QS'),('approved', 'PM'),('done', 'Done'),('cancel', 'Cancel')], default="draft", string="Status")
	partner_id = fields.Many2one('res.partner', required=True, string="Vendor")

	spb_line_ids = fields.One2many('spb.line', 'spb_id')

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('spb.sequence') or '/'
		return super(spb, self).create(vals)

	@api.multi
	def unlink(self):
		for order in self:
			if order.states in ('approved', 'done'):
				raise UserError(_('You cannot delete a approved SPB.'))
		return super(spb, self).unlink()

class SPBLine(models.Model):
	
	_name = 'spb.line'

	name = fields.Char(string="Description")
	product_id =  fields.Many2one('product.product', required=True, string="Product")
	satuan = fields.Many2one('product.uom', string="Satuan")
	jumlah_permintaan = fields.Float(digits=dp.get_precision('Product Unit of Measure'), string="Jumlah Permintaan")
	account_analytic = fields.Many2one('account.analytic.account', string="Account Analytic") 
	quantity_transfer = fields.Float(digits=dp.get_precision('Product Unit of Measure'), readonly=True, string="Quantity Transfer")
	quantity_po = fields.Float(digits=dp.get_precision('Product Unit of Measure'), readonly=True, string="Quantity PO")
	outstanding_spb = fields.Float(digits=dp.get_precision('Product Unit of Measure'), readonly=True, string="Outstanding SPB")

	states = fields.Selection(related="spb_id.states", store=True, default="draft", string="Status")

	spb_id = fields.Many2one('spb')

	@api.depends('jumlah_permintaan','quantity_transfer','quantity_po')
	def sum_outstanding_spb(self):
		for record in self:
			record.outstanding_spb = record.jumlah_permintaan-(record.quantity_transfer+record.quantity_po)

	@api.onchange('product_id')
	def description_product(self):
		result = {}
		if not self.product_id:
			return result

		self.satuan = self.product_id.uom_po_id or self.product_id.uom_id
		result['domain'] = {'satuan': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
		product_lang = self.product_id.with_context(
			lang=self.env.user.lang
		)
		self.name = product_lang.display_name

		return result

class SPBWizard(models.TransientModel):
	
	_name = 'spb.wizard'

	name = fields.Char()
	pilihan_wizard = fields.Selection([('po','Purchase Order'),('io','Inventory Order')])
	buat_baru = fields.Selection([('yes','Yes'),('no','No')])