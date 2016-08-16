# -*- coding: utf-8 -*-
{
    'name': "预算管理",

    'summary': """
        对员工的差旅费、日常费用、专项费用、平台费用进行预算管理。""",

    'description': """
            按部门、按员工进行最小单位预算申报，能按预算管理的时间要求进行系统提醒，可以查询到某月哪个部门的哪些员工还没提交预算申请，可以邮件提醒，
        督促及时完成；  主要针对各部门员工预计发生的差旅费（包括手机话费、市内交通费）、日常费用、专项费用、平台费用等进行预算管理。
            每个月每个员 工只能提交一次预算申请。提交时需记录操作日志。邮件提醒审批人。
    """,

    'author': "东南飞",
    'website': "http://www.dtdream.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','dtdream_expense'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_view.xml',
        'views/views.xml',
        'workflow/workflow.xml',
        'views/templates.xml',
        'importjscss.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}