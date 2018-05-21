# -*- coding: utf-8 -*-
{
    'name'      : "Totalindo Rekruitment",
    'version'   : '1.1',
    'summary'   : 'Rekruitment Module',
    'sequence'  : 30,
    'author'    : "Dion Martin",
    # 'website'   : "http://odooabc.com",
    'category'  : 'Human Resource',
    'depends'   : ['base','hr','hr_recruitment'],
    'data'      : [
            'views/hr_applicant_view.xml',
    ],
    'demo': [
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
