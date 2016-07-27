# -*- coding: utf-8 -*-
{
    'name': "dtdream_customer_reception",

    'summary': """
        申请客户接待资源""",

    'description': """
        各类客户到公司参观、拜访等活动前，由此电子流申请客户接待资源!
    """,

    'author': "jsz",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/importcss.xml',
        'views/actions.xml',
        'views/menu.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}