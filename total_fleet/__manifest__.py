# -*- coding: utf-8 -*-
{
    'name'      : "Totalindo Fleet",
    'version'   : '1.1',
    'summary'   : 'Inherit Fleet Module',
    'sequence'  : 30,
    'author'    : "Dion Martin",
    # 'website'   : "http://odooabc.com",
    'category'  : 'Human Resource',
    'depends'   : ['base','fleet'],
    'data'      : [
            'views/fleet_view.xml',
            'views/mutasi_kendaraan_view.xml',
    ],
    'demo': [
    ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
