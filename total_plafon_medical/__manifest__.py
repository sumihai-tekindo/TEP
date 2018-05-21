# -*- coding: utf-8 -*-
{
    'name'      : "Totalindo Plafon Medical",
    'version'   : '1.1',
    'summary'   : 'Plafon Medical',
    'sequence'  : 30,
    'author'    : "Dion Martin",
    # 'website'   : "http://odooabc.com",
    'category'  : 'Human Resource',
    'depends'   : ['base','hr','hr_expense'],
    'data'      : [
            'views/hr_employee_view.xml',
            'views/hr_expense_view.xml',
            'views/hr_plafon_medical_view.xml',
    ],
    'demo': [
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
