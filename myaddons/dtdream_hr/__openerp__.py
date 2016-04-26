# -*- coding: utf-8 -*-
{
    'name': "数梦部门和员工管理",

    'summary': """
        部门和员工管理
        """,

    'description': """
        部门和员工管理
    """,

    'author': "小毅",
    'website': "www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/department_views.xml',
        'views/employee_views.xml',
        'security/dtdream_hr_security.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}