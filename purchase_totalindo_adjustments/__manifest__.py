# -*- coding: utf-8 -*-
{
    'name': "Purchase Totalindo Adjustments",

    'summary': """
        This module is modifying the inventory adjustments form in this application""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Sumihai Teknologi Indonesia",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase',
        'hr_timesheet',
        'stock',
        'account',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/inventory_adjustments.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}