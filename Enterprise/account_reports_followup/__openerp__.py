# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Follow-up Management',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
Module to automate letters for unpaid invoices, with multi-level recalls.
=========================================================================

You can define your multiple levels of recall through the menu:
---------------------------------------------------------------
    Configuration / Follow-up / Follow-up Levels
    
Once it is defined, you can automatically print recalls every day through simply clicking on the menu:
------------------------------------------------------------------------------------------------------
    Payment Follow-Up / Send Email and letters

It will generate a PDF / send emails / set manual actions according to the the different levels 
of recall defined. You can define different policies for different companies. 

Note that if you want to check the follow-up level for a given partner/account entry, you can do from in the menu:
------------------------------------------------------------------------------------------------------------------
    Reporting / Accounting / **Follow-ups Analysis

""",
    'author': 'OpenERP SA',
    'website': 'https://www.odoo.com/page/billing',
    'depends': ['account_accountant', 'mail', 'account_reports', 'account_extension'],
    'data': [
        'security/account_followup_security.xml',
        'security/ir.model.access.csv',
        'account_followup_company.xml',
        'account_followup_data.xml',
        'account_followup_view.xml',
        'res_config_view.xml',
        'views/report_followup.xml',
    ],
    'demo': ['account_followup_demo.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'OEEL-1',
}
