# -*- coding: utf-8 -*-
{
    'name': "dtdream_limited_login",

    'summary': """
        限制用户登录次数""",

    'description': """
        对用户登录次数进行限制，失败一定次数后锁定改账户，锁定后无法登录，管理员可以解除该锁定。
    """,

    'author': "东南飞",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}