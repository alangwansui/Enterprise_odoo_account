# -*- coding: utf-8 -*-
{
    'name': "专项审批",

    'summary': """
        专项业务申请与审批""",

    'description': """
        Long description of module's purpose
    """,

    'author': "小池",
    'website': "http://www.dtdream.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail','base','web','hr','dtdream_sale'],

    # always loaded
    'data': [
        'data/timingData.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/dtdream_special_wizard.xml',
        'views/configureViews.xml',
        'views/views.xml',
        'views/templates.xml',
        'workflow/workflow.xml',
        'views/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}