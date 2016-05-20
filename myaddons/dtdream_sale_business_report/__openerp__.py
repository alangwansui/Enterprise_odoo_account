# -*- coding: utf-8 -*-
{
    'name': "dtdream_sale_business_report",

    'summary': """
        新增商务报备申请流程""",

    'description': """
        新增商务报备申请流程，包括商务审批配置，商务报备字段、表单新增，商务报备与项目管理关联、商务报备流程定义。
    """,

    'author': "Dtdream",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','crm','dtdream_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/actions.xml',
        'views/menus.xml',
        'workflow/workflow.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}