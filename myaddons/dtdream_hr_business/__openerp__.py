# -*- coding: utf-8 -*-
{
    'name': "外出公干",

    'summary': """
    外出公干，外出公干的审批""",

    'description': """
        外出公干，外出公干的审批
    """,

    'author': "小池",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','mail','base','web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
         'security/security.xml',
        'wizard/business_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
        'workflow/workflow.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}