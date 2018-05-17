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
        'purchase',
        'hr_timesheet',
        'stock',
    ],
    'data': [
        'data/data.xml',
        'views/purchase_config_setting_view.xml',
        'views/spb_view.xml',
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'active': False,
    'application': True,
}