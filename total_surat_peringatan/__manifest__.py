# -*- coding: utf-8 -*-
{
    'name'      : "Totalindo Surat Peringatan",
    'version'   : '1.1',
    'summary'   : 'Module Surat Peringatan',
    'sequence'  : 30,
    'author'    : "Dion Martin",
    # 'website'   : "http://odooabc.com",
    'category'  : 'Human Resource',
    'depends'   : ['base','hr'],
    'data'      : [
            'views/surat_peringatan_views.xml',
            'data/scheduler_sp.xml',
    ],
    'demo': [
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
