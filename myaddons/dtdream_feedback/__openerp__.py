# -*- coding: utf-8 -*-
{
    'name': "dtdream_feedback",

    'summary': """
        意见反馈
        """,

    'description': """
        该模块用于用户反馈意见
        """,

    'author': "苏志勇",
    'website': "http://www.dtdream.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'workflow/workflow.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
     'qweb': [

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
