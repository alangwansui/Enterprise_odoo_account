# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import openerp.tests

@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):
    def test_ui(self):
        self.phantom_js("/", "odoo.__DEBUG__.services['web.Tour'].run('account_followup_reports_widgets_2', 'test')", "odoo.__DEBUG__.services['web.Tour'].tours.account_followup_reports_widgets_2", login='admin')