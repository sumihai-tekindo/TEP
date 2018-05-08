{
    "name": "Reverse Cancelled Invoice",
    "version": "10.1",
    "depends": [
        'account_cancel',
    ],
    "author": "Joenan <joenannr@gmail.com>",
    "category": "",
    "description" : """Reverse cancelled invoice instead of delete its journal entry""",
    'data': [
        "views/account_view.xml",
    ],
    'demo':[     
    ],
    'test':[
    ],
    'application' : False,
    'installable' : True,
    'auto_install' : False,
}
