# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
import logging
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def get_next_char(self, number_next):
        res = super(IrSequence, self).get_next_char(number_next)
        if self._context.get('prefix') or self._context.get('suffix'):

            def _interpolate(s, d):
                return (s % d) if s else ''
     
            def _interpolation_dict():
                now = range_date = effective_date = datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
                if self._context.get('ir_sequence_date'):
                    effective_date = datetime.strptime(self._context.get('ir_sequence_date'), '%Y-%m-%d')
                if self._context.get('ir_sequence_date_range'):
                    range_date = datetime.strptime(self._context.get('ir_sequence_date_range'), '%Y-%m-%d')
     
                sequences = {
                    'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
                    'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S'
                }
                res = {}
                for key, format in sequences.iteritems():
                    res[key] = effective_date.strftime(format)
                    res['range_' + key] = range_date.strftime(format)
                    res['current_' + key] = now.strftime(format)
     
                return res
     
            d = _interpolation_dict()
            prefix = self.prefix.replace('###', self._context.get('prefix')) if self._context.get('prefix') else self.prefix
            suffix = self.suffix.replace('###', self._context.get('suffix')) if self._context.get('suffix') else self.suffix
            try:
                interpolated_prefix = _interpolate(prefix, d)
                interpolated_suffix = _interpolate(suffix, d)
            except ValueError:
                raise UserError(_('Invalid prefix or suffix for sequence \'%s\'') % (self.get('name')))
            return interpolated_prefix + '%%0%sd' % self.padding % number_next + interpolated_suffix
        else:
            return res
