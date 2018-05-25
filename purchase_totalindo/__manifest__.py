# -*- coding: utf-8 -*-
{
    'name': "Purchase Totalindo",
    'summary': """ SPB, PO """,
    'description': """ This module for SPB, PO """,
    'author': "Sumihai Teknologi Indonesia",
    'website': "http://www.sumihai.co.id",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'purchase',
        'hr_timesheet',
        'stock',
        'mail'
    ],
    'data': [
        'data/data.xml',
        'views/purchase_config_setting_view.xml',
        'views/spb_view.xml',
        'views/purchase_order_view.xml',
        'views/company_view.xml',
        'report/spb_report.xml',
        'report/spb_report_templates.xml',
    ],
    'installable': True,
    'active': False,
    'application': True,
}