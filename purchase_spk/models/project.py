from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"
    
    spk_sequence_id = fields.Many2one('ir.sequence', string='SPK Sequence', required=True)
    om_sequence_id = fields.Many2one('ir.sequence', string='Opname Mandor Sequence', required=True)
