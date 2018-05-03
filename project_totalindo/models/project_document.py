import hashlib
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class ProjectDocument(models.Model):
    _name = 'project.document'
    _description = 'Document'
    _inherits = {'ir.attachment': 'attachment_id'}
    
    attachment_id = fields.Many2one('ir.attachment', 'Attachment',
        auto_join=True, index=True, ondelete="cascade", required=True)
    project_id = fields.Many2one('project.project', string='Project')
    category = fields.Selection([('db', 'DB'),
                                 ('dbb', 'DBB')], string='Category')
    date = fields.Date(string='Date')
    type = fields.Many2one('project.document.type', string='Document Type')
    department = fields.Many2one('hr.department', string='Department')
    version = fields.Char(string='Version')
    image_number = fields.Char(string='Image Number')
    approve_by = fields.Char(string='Approve by')


class ProjectDocumentType(models.Model):
    _name = "project.document.type"
    _description = 'Document Type'
    
    name = fields.Char(string='Name', required=True)
    
