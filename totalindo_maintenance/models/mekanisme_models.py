from odoo import models, fields, api

class mekanisme_maintenance(models.Model):
	_name = 'mekanisme.maintenance'

	mekanisme_line = fields.One2many('mekanisme.detail', 'mekanisme_id')

class mekanisme_detail(models.Model):
	_name = 'mekanisme.detail'

	mekanisme_id = fields.Many2one('mekanisme.maintenance')
	equipment = fields.Many2one('maintenance.equipment',string='Equipment')
	mekanisme = fields.Many2one('mekanisme.name', string='Mekanisme')

class mekanisme_name(models.Model):
	_name = 'mekanisme.name'

	name = fields.Char('Name')

class preventive_maintenance(models.Model):
	_name = 'preventive.maintenance'
	
	preventive_line = fields.One2many('preventive.detail', 'preventive_id')

class preventive_detail(models.Model):
	_name = 'preventive.detail'

	preventive_id = fields.Many2one('preventive.maintenance')
	equipment = fields.Many2one('maintenance.equipment',string='Equipment')
	mekanisme = fields.Many2one('mekanisme.name', string='Mekanisme')
	jenis_pekerjaan = fields.Char(string="Jenis Pekerjaan")
	jam_kerja = fields.Many2one('jam.kerja', string="Jam Kerja")

class jam_kerja(models.Model):
	_name = 'jam.kerja'

	jam_line = fields.One2many('jam.detail', 'jam_id')

class jam_detail(models.Model):
	_name = 'jam.detail'

	jam_id = fields.Many2one('jam.kerja')
	name = fields.Integer('Jam Kerja')