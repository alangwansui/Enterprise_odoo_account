# -*- coding: utf-8 -*-
{
    'name': "dtdream_rd_prod",

    'summary': """
        研发产品""",

    'description': """
        该模块是新创建的，不继承原有模块，主要解决研发产品的立项审批与进度跟踪
    """,

    'author': "小池",
    'website': "http://www.dtdream.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
