# -*- coding: utf-8 -*-
{
    'name': "dtdream_hr_holidays_extend",

    'summary': """
        继承dtdream_hr_holidays""",

    'description': """
        改写成适合本公司请假流程
    """,

    'author': "周旋",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_holidays'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/views.xml',
        'security/security.xml',
        'views/templates.xml',
        # 'data/data.xml',
        'workflow.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',

    ],
}