# -*- coding: utf-8 -*-
{
    'name': "资产管理",

    'summary': """
        资产管理""",

    'description': """
        用于员工资产盘点
    """,

    'author': "shumeng",
    'website': "www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'wizard/dtdream_assets_management_wizard.xml',
        'views/dtdream_assets_check.xml',
        'workflow/dtdream_assets_check_workflow.xml',
        'views/dtdream_assets_store_place.xml',
        'views/dtdream_assets_supply.xml',
        'views/dtdream_assets_name.xml',
        'views/dtdream_assets_management.xml',
        'views/data.xml',
        'security/ir.model.access.csv',
    ],
}