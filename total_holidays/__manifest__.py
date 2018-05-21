# -*- coding: utf-8 -*-
{
    'name'      : "Totalindo Leaves",
    'version'   : '1.1',
    'summary'   : 'Inherit Leave Module',
    'sequence'  : 30,
    'author'    : "Dion Martin",
    # 'website'   : "http://odooabc.com",
    'category'  : 'Human Resource',
    'depends'   : ['base','hr','hr_holidays'],
    'data'      : [
            'views/hr_holidays_view.xml',
            'views/generate_leaves_view.xml',
    ],
    'demo': [
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
