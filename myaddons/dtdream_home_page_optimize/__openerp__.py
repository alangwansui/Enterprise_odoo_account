# -*- coding: utf-8 -*-
{
    'name': "dodo主页优化",

    'summary': """
        优化dodo主页""",

    'description': """
        dodo主页重新设计优化
    """,

    'author': "dtdream",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web'],

    # always loaded
    'data': [
         # 'views/home_page.xml',
    ],

    'qweb': [
        'views/home_page.xml',
    ],
}