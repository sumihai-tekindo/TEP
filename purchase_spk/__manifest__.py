# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2011-2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Purchase Service (SPK)',
    'description': '''Project Management for Totalindo''',
    'version': '10.1.0',
    'category': 'Project',
    'author': "Joenan <joenannr@gmail.com>",
    'license': 'AGPL-3',
    'website': 'https://arkana.co.id',
    'depends': [
        'purchase',
        'project',
        'base_sequence_custom',
    ],
    'data': [
        'views/res_config_views.xml',
        'views/project_views.xml',
        'views/spk_views.xml',
        'views/opname_views.xml',
        'views/recap_views.xml',
    ],
    'installable': True,
    'active': False,
    'application': True,
}
