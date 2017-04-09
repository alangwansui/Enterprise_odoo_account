# -*- coding: utf-8 -*-
{
    'name': "dtdream_sale_contract_fee",

    'summary': """
        增加市场合同模块""",

    'description': """
        增加市场合同模块
    """,

    'author': "泸江",
    'website': "dodo.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions.xml',
        'views/menus.xml',
        'views/views.xml',
        'views/contract_details.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}