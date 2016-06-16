# -*- coding: utf-8 -*-
{
    'name': "dtdream_hr_performance",

    'summary': """
        员工绩效管理""",

    'description': """
        employee performance manage
    """,

    'author': "jinshuzhao",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions.xml',
        'views/menu.xml',
        'views/views.xml',
        'views/templates.xml',
        'workflow/workflow.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
