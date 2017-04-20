# -*- coding: utf-8 -*-
{
    'name': "dtdream_sale_weekly_report",

    'summary': """
        增加市场周报""",

    'description': """
        增加市场周报，包括个人周报、主管周报。
    """,

    'author': "Dtdream",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','dtdream_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/weekly_report_security.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/views.xml',
        'views/data.xml',
        'views/templates.xml',
        'importcss.xml',
        'views/ding_report_config.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}