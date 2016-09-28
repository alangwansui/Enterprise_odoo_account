# -*- coding: utf-8 -*-
{
    'name': "客户接待",

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

    'depends': ['base', 'hr', 'crm', 'dtdream_special_approval'],

    # always loaded
    'data': [
        'views/data.xml',
        'views/importcss.xml',
        'views/actions.xml',
        'views/menu.xml',
        'wizard/customer_reception_wizard.xml',
        'views/views.xml',
        'workflow/workflow.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
