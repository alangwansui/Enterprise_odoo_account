# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.tests import common


class TestAccountReports(common.TransactionCase):

    def test_00_financial_reports(self):
        for report in self.env['account.financial.html.report'].search([]):
            context_data = self.env['account.report.context.common'].return_context('account.financial.html.report', {}, report.id)
            self.env[context_data[0]].browse(context_data[1]).get_html_and_data()

    def test_01_custom_reports(self):
        report_models = [
            'account.bank.reconciliation.report',
            'account.general.ledger',
            'account.generic.tax.report',
        ]
        for report_model in report_models:
            context_data = self.env['account.report.context.common'].return_context(report_model, {})
            self.env[context_data[0]].browse(context_data[1]).get_html_and_data()

    def test_02_followup_reports(self):
        self.env['account.report.context.followup.all'].create({}).get_html({'page': 1})
        self.env['account.report.context.followup'].create({'partner_id': self.env.ref('base.res_partner_2').id}).get_html()
