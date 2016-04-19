# -*- coding: utf-8 -*-
{
    'name': "离职电子流",

    'summary': """
        离职电子流，包含离职审批和工作交接流程
        """,

    'description': """
        离职电子流，包含离职审批和工作交接流程
    """,

    'author': "小毅",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['dtdream_hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'wizard/leaving_handle_wizard.xml',
        'views/leaving_handle.xml',
        'views/leaving_process.xml',
        'views/leaving_handle_approver.xml',
        # 'data/data.xml',
        'workflow/workflow.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}