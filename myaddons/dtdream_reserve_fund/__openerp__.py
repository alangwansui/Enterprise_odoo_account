# -*- coding: utf-8 -*-
{
    'name': "备用金管理",

    'summary': """
        员工因业务需求，预先借支/预付备用金，款项支付到员工/供应商，取得发票后通过dodo报销进行核销。""",

    'description': """
        员工因业务需求，预先借支/预付备用金，款项支付到员工/供应商，取得发票后通过dodo报销进行核销。
    """,

    'author': "0569",
    'website': "http://www.dtdream.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'dtdream_hr', 'dtdream_special_approval'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/reserve_fund_dashboard.xml',
        'views/dtdream_reserve_sign.xml',
        'views/dtdream_reserve_record_config.xml',
        'sequence/dtdream_reserve_fund_sequence.xml',
        'views/dtdream_reserve_wizard.xml',
        'views/dtdream_reserve_fund_view.xml',
        'views/dtdream_reserve_position.xml',
        'views/js_css.xml',
        'workflow/workflow.xml',
        'views/templates.xml',
        'print/dtdream_reserve_fund_report.xml',
        'views/regularly_compute_out_time.xml',
    ],
    'qweb': [
        # "static/src/xml/*.xml",
        'static/src/xml/reserve_fund_dashboard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
