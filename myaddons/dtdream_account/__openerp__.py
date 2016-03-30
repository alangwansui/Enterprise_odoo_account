# -*- coding: utf-8 -*-
{
    'name': "数梦会计",

    'summary': """
        数梦会计""",

    'description': """
        增加科目类型菜单
        会计分录里增加字段
    """,

    'author': "小毅",
    'website': "www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['dtdream_hr','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}