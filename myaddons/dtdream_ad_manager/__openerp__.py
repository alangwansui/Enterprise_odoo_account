# -*- coding: utf-8 -*-
{
    'name': "dtdream_ad_manager",

    'summary': """
        域信息管理
        """,

    'description': """
        该模块用于公司域账号、群组管理。
        """,

    'author': "苏志勇",
    'website': "http://www.dtdream.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'dtdream_hr', 'mail'],

    # always loaded
    'data': [
        'workflow/workflow.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/dtdream_ad_department.xml',
        'views/dtdream_ad_ext.xml',
        'views/dtdream_ad_man.xml',
        'data/timingData.xml'
    ],
     'qweb': [

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
