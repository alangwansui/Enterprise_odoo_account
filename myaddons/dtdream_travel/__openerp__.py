# -*- coding: utf-8 -*-
{
    'name': "dtdream_travel",

    'summary': """出差申请""",

    'description': """
        出差申请,包括出差申请单创建，删除，审批
    """,

    'author': "jsz",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'travel',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/chucha_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/actions.xml',
        'views/menu.xml',
        'workflow/workflow.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}