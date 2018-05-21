# -*- coding: utf-8 -*-
{
    'name'      : "Totalindo Employee",
    'version'   : '1.1',
    'summary'   : 'Inherit Employee Module',
    'sequence'  : 30,
    'author'    : "Dion Martin",
    # 'website'   : "http://odooabc.com",
    'category'  : 'Human Resource',
    'depends'   : ['base','hr','hr_expense'],
    'data'      : [
            'views/hr_employee_view.xml',
            'views/hr_mutasi_view.xml',
            'views/hr_phk_view.xml',
    ],
    'demo': [
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
