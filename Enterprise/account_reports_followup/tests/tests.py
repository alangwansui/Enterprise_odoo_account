# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.tests import common


class TestAccountFollowupReports(common.TransactionCase):

    def test_00_followup_reports(self):
        self.env['account.report.context.followup.all'].create({}).get_html({'page': 1})
        self.env['account.report.context.followup'].create({'partner_id': self.env.ref('base.res_partner_2').id}).get_html()
