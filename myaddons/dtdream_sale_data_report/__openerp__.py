# -*- coding: utf-8 -*-
{
    'name': "dtdream_sale_data_report",

    'summary': """
        增加销售报表模块""",

    'description': """
        增加销售报表模块
    """,

    'author': "泸江",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','dtdream_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/department_province.xml',

    ],
    'qweb': [
        # "static/src/xml/*.xml",
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}