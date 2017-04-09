# -*- coding: utf-8 -*-
{
    'name': "dtdream_project_bid_authorize_apply",

    'summary': """
        项目招投标授权申请""",

    'description': """
        本应用于完成整个项目招投标授权申请流程。
    """,

    'author': "My Company",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','sale','hr','stock','sale_crm','dtdream_sale_business_report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/wizard.xml',
        'views/views.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/templates.xml',
        'workflow/workflow.xml',
        'security/ir.model.access.csv',
        'importcss.xml'

        # 'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}