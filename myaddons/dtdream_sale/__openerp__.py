# -*- coding: utf-8 -*-
{
    'name': "dtdream_sale",

    'summary': """
        增加销售管理模块的数梦工场特性""",

    'description': """
    增加销售管理模块的数梦工场特性，包括新增字段，增加行业、区域等多个维度的权限管理，增加行业、办事处配置项。
    """,

    'author': "Dtdream",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/industry_office.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}