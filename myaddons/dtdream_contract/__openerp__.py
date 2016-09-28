# -*- coding: utf-8 -*-
{
    'name': "dtdream_contract",

    'summary': """
        数梦合同评审电子流""",

    'description': """
        新建模块，用于合同评审
    """,

    'author': "周旋",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','crm','web','dtdream_sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
         'dtdream_contract_wizard.xml',
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
        'dtdream_contract_workflow.xml',
        'importjs.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}