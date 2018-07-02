# -*- coding: utf-8 -*-
{
    'name'      : "Totalindo Kost Management",
    'version'   : '1.1',
    'summary'   : 'Kost Management Module',
    'sequence'  : 30,
    'author'    : "Dion Martin",
    # 'website'   : "http://odooabc.com",
    'category'  : 'Human Resource',
    'depends'   : ['base','hr'],
    'data'      : [
            'views/list_kost_view.xml',
            'views/sewa_kost_view.xml'
    ],
    'demo': [
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
