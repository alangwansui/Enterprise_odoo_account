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
    'depends': ['base','hr','web'],

    # always loaded
    'data': [
        'wizard/lixiang_wizard.xml',
        'wizard/process_wizard.xml',
        'wizard/dtdream_suspension_wizard.xml',
        'wizard/dtdream_suspension_restoration_wizard.xml',
        'wizard/dtdream_termination_wizard.xml',

        'security/security.xml',
        'security/ir.model.access.csv',

        'views/replanning.xml',
        'views/dtdream_execption.xml',
        'views/dtdream_rd_config.xml',
        'views/dtdream_rd_PDTconfig.xml',
        'views/dtdream_rd_riskconfig.xml',
        'views/dtdream_rd_risksortconfig.xml',
        'views/dtdream_rd_approver.xml',
        'views/dtdream_rd_approver_ver.xml',
        'views/dtdream_rd_process.xml',
        'views/dtdream_rd_process_ver.xml',
        'views/dtdream_prod_suspension.xml',
        'views/dtdream_prod_suspension_restoration.xml',
        'views/dtdream_prod_termination.xml',



        'views/dtdream_rd_dashboard.xml',

        'views/version_view.xml',
        'views/views.xml',
        'views/templates.xml',

        'workflow/replanningWkf.xml',
        'workflow/workflow.xml',
        'workflow/versionWorkflow.xml',

        'data/timingData.xml',

        'import.xml',

    ],
     'qweb': [
        'views/rd_dashboard_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
