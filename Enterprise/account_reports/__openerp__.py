# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Accounting Reports',
    'author' : 'Odoo SA',
    'summary': 'View and create reports',
    'description': """
Accounting Reports
====================
    """,
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/init.yml',
        'data/account_financial_report_data.xml',
        'views/account_report_view.xml',
        'views/report_financial.xml',
        'views/report_followup.xml',
        'views/company_view.xml',
        'views/partner_view.xml',
        'views/account_journal_dashboard_view.xml',
    ],
    'qweb': [
        'static/src/xml/account_report_backend.xml',
    ],
    'auto_install': True,
    'installable': True,
    'license': 'OEEL-1',
}
