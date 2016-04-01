# -*- coding: utf-8 -*-
{
    'name': "Account Extension",
    'description': """
        Adapt base accounting module for Enterprise Edition.

        This module will be auto installed if account module and enterprise edition are present
    """,
    'author': "Odoo SA",
    'category': 'Hidden',
    'version': '1.0',
    'depends': ['account'],
    'data': [
        'views/account_report_menu_invisible.xml',
        'views/res_config_view.xml',
    ],
    'auto_install': True,
    'license': 'OEEL-1',
}
