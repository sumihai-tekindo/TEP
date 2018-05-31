# -*- coding: utf-8 -*-
{
    'name': "Totalindo Maintenance",

    'summary': """
        Developed by PT. Sumihai Teknologi Indonesia - Official Partner of Odoo""",

    'description': """
        Modul ini merupakan hasil pembuatan dari tim IT Developer
        PT. Sumihai Teknologi Indonesia. Modul ini berisi tentang
        informasi yang dibutuhkan oleh PT. Totalindo Eka Persada
        untuk menu Maintenance
    """,

    'author': "Yodi Safikri",
    'website': "http://www.yodisafikri.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Maintenance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'maintenance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mekanisme_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}