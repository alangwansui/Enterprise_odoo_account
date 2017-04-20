# -*- coding: utf-8 -*-
{
    'name': "dtdream_common_manage",

    'summary': """
        通用管理
        """,

    'description': """
        该模块用于公司邮箱、门禁、VPN等通用申请的管理。
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
        'security/ir.model.access.csv',
        'workflow/workflow.xml',
        'views/views.xml',
        'data/timingData.xml'
    ],
     'qweb': [

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
