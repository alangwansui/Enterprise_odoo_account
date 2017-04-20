# -*- coding: utf-8 -*-
{
    'name': "dtdream_hr_infor",

    'summary': """员工基础信息,员工自助信息""",

    'description': """
        员工基础信息,员工自助信息
    """,

    'author': "jinshuzhao",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'workflow/workflow.xml',
        'wizard/hr_travel_grant_wizard.xml',
        'wizard/hr_bank_wizard.xml',
        'wizard/hr_mobile_fee_wizard.xml',
        'views/setting.xml',
        'views/views.xml',
        'views/data.xml',
        'views/bank_info.xml',
        'views/mobile_fee.xml',
        'views/travel_grant.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}