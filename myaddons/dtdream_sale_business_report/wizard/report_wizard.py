# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime

class ReportWizard(models.TransientModel):
    _name = 'dtdream.report.wizard'

    liyou = fields.Text("意见", required=True)

    @api.one
    def btn_confirm(self):
        current_report = self.env['dtdream.sale.business.report'].browse(self._context['active_id'])
        state_name =dict(self.env['dtdream.sale.business.report']._columns['state'].selection)[current_report.state]
        shenpiren_name = self.env['hr.employee'].search([('login','=',self.env.user.login)]).name
        self.env['report.handle.approve.record'].create({"name":state_name,"result":"驳回","shenpiren":shenpiren_name, "liyou":self.liyou,"report_handle_id":self._context['active_id']})
        current_report.signal_workflow('btn_reject')

class ReportApproveWizard(models.TransientModel):
    _name = 'dtdream.report.approve.wizard'

    liyou = fields.Text("意见")

    @api.one
    def btn_confirm(self):
        current_report = self.env['dtdream.sale.business.report'].browse(self._context['active_id'])
        state_name =dict(self.env['dtdream.sale.business.report']._columns['state'].selection)[current_report.state]
        shenpiren_name = self.env['hr.employee'].search([('login','=',self.env.user.login)]).name
        self.env['report.handle.approve.record'].create({"name":state_name,"result":"通过","shenpiren":shenpiren_name, "liyou":self.liyou,"report_handle_id":self._context['active_id']})
        current_report.signal_workflow('btn_approve')