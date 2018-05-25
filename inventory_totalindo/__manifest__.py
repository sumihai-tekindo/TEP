# -*- coding: utf-8 -*-
{
    'name': "Inventory Totalindo",
    'summary': """ SPM (Receipt), Surat Jalan (Internal Transfer), Bon Masuk, Bon Keluar, Inventory Adjustments """,
    'description': """ This module is connected to Purchase Totalindo """,
    'author': "Sumihai Teknologi Indonesia",
    'website': "http://www.sumihai.co.id",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'purchase_totalindo',
        'hr_timesheet',
        'stock',
        'account',
    ],
    'data': [
        'data/data.xml',
        'views/inventory_adjustments_view.xml',
    ],
    'installable': True,
    'active': False,
    'application': True,
}