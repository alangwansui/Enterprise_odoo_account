# -*- coding: utf-8 -*-
{
    'name': "shumeng",

    'summary': """
        1111111""",

    'description': """
        222222
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'study',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        
        'security/security.xml',
        'security/ir.model.access.csv',
        
        'wizard/wizard.xml',
        'wizard/qj_wizard.xml',

        #'views/pre_actions.xml',
        'report/course_report_view.xml',

        'views/views.xml',
        'views/course_exam.xml',
        'views/teachers.xml',
        'views/res_users.xml',

        'views/actions.xml',
        'views/menus.xml',

        'workflow/workflow.xml',

        'templates/templates.xml',
        'templates/reports.xml',

        'sequence.xml',

        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
