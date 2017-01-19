# -*- coding: utf-8 -*-
{
    'name': "信息安全",

    'summary': """
        为保护公司信息安全""",

    'description': """
        为保护公司信息安全，各种机密性不同的信息查看要申请批准后才可以查看
    """,

    'author': "小池",
    'website': "http://www.dtdream.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','mail'],

    # always loaded
    'data': [
        'data/timingData.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/dtdream_information_purview_wizard.xml',
        'wizard/dtdream_information_shouquan_wizard.xml',
        'wizard/dtdream_foreign_wizard.xml',
        'views/dtdream_information_people.xml',
        'views/dtdream_information_security_depart.xml',
        'views/dtdream_information_type.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/dtdream_foreign.xml',
        'workflow/dtdream_information_purview_wkf.xml',
        'workflow/dtdream_foreign_workflow.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}