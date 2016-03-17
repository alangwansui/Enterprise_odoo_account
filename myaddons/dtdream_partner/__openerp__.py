# -*- coding: utf-8 -*-
{
    'name': "dtdream_partner",

    'summary': """
        增加客户管理模块的数梦工场特性
        """,

    'description': """
        增加客户管理模块的数梦工场特性，包括新增字段，增加行业、区域两个维度的权限管理，增加客户营销活动管理等。
    """,

    'author': "Dtdream",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'sale',
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