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
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/expense_wizard_reject.xml',
        'wizard/expense_wizard_agree.xml',

        'views/dtdream_expense_record.xml',
        'views/dtdream_expense_report.xml',
        'views/dtdream_expense_catelog.xml',
        'views/dtdream_expense_detail.xml',
        'views/dtdream_expense_president.xml',
        'views/dtdream_expense_quanqian.xml',
        'views/dtdream_expense_city.xml',
        'views/dtdream_expense_province.xml',

        'workflow/expenseworkflow.xml',
        'views/expense_data.xml',
        'print/dtdream_expense_report.xml',
        'importcssjs.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}