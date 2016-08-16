# -*- coding: utf-8 -*-
{
    'name': "dtdream_expense",

    'summary': """
        数梦费用报销流程""",

    'description': """
       消费记录上传，费用报销单的提交，审批，工作委托，授权。
    """,

    'author': "杭州数梦工场",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['dtdream_hr','base'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
        'wizard/expense_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
        'workflow/expenseworkflow.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}