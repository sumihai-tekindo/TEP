# -*- coding: utf-8 -*-
{
    'name'      : "Totalindo Payroll",
    'version'   : '1.1',
    'summary'   : 'HR Payroll',
    'sequence'  : 30,
    'author'    : "Dion Martin",
    # 'website'   : "http://odooabc.com",
    'category'  : 'Human Resource',
    'depends'   : ['base','hr','hr_payroll'],
    'data'      : [
            'data/hr_rule_data.xml',
    ],
    'demo': [
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
