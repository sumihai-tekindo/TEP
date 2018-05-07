# -*- coding: utf-8 -*-
{
    'name': "Accounting Totalindo",

    'summary': """
        Developed by PT. Sumihai Teknologi Indonesia - Official Partner of Odoo""",

    'description': """
        Modul ini merupakan hasil pembuatan dari tim IT Developer
        PT. Sumihai Teknologi Indonesia. Modul ini berisi tentang
        informasi yang dibutuhkan oleh PT. Totalindo Eka Persada
        untuk menu kontrak
    """,

    'author': "Yodi Safikri",
    'maintainer': "Yodi Safikri - yodi.safikri@sumihai.co.id",
    'website': "http://www.yodisafikri.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting Totalindo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}