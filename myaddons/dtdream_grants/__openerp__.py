# -*- coding: utf-8 -*-
{
    'name': "补助金管理",

    'summary': """
        对发放给员工的补助金实现自助式管理，分管理界面与自主界面。""",

    'description': """
        员工在任何时候，在“补助金充值设置”页面上设置充值金额，系统每月1日按每位员工的充值设置，自动生成上月的充值记录，每人每月一条记录。
        hr每月1日后从系统导出所有员工上月数据，分别给行政、财务等部门，进行实际的充值操作。
    """,

    'author': "东南飞",
    'website': "http://www.dtdream.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','dtdream_hr_leaving'],

    # always loaded
    'data': [

        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/templates.xml',
        'create_allocation_regularly_data.xml',
        'import.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}