# -*- coding: utf-8 -*-
{
    'name': "项目管理",

    'summary': """服务部项目管理""",

    'description': """
        The project-manage for shumeng's server department.
    """,

    'author': "dtdream",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': '服务',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/dtdream_project_stage.xml',
        'views/dtdream_project_plan_config.xml',
        'views/dtdream_project_order.xml',
        'views/dtdream_project_role.xml',
        'views/dtdream_project_manage.xml',
        'views/data.xml',
        'views/workflow.xml',
        'views/dtdream_pmoo_wizard.xml',
    ],
}
