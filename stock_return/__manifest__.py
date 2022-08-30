# -*- coding: utf-8 -*-
{
    'name': "Stock Return Operation",

    'summary': """
        Stock Return Operation""",

    'description': """
        Stock Return Operation
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Inventory',
    'version': '13.1.0.0',

    'depends': ['base', 'stock'],

    'data': [
        'data/stock_data.xml',
    ],
    'demo': [
    ],
    'post_init_hook': '_auto_install_l10n',
}
