# -*- coding: utf-8 -*-
{
    'name'      : "Totalindo Pinjaman Karayawan",
    'version'   : '1.1',
    'summary'   : 'Pinjaman Karyawan Module',
    'sequence'  : 30,
    'author'    : "Dion Martin",
    # 'website'   : "http://odooabc.com",
    'category'  : 'Human Resource',
    'depends'   : ['base','hr'],
    'data'      : [
            'views/pinjaman_karyawan_view.xml',
    ],
    'demo': [
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
