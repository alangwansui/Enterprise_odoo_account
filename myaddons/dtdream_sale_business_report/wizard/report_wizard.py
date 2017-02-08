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
        self.env['report.handle.approve.record'].create({"shenpiren_version":current_report.shenpiren_version,"name":state_name,"result":"驳回","shenpiren":shenpiren_name, "liyou":self.liyou,"report_handle_id":self._context['active_id']})
        current_report.write({'approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        if current_report.state in ('1','2','3'):
            current_report.write({'product_approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        else :
            current_report.write({'business_approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        current_report.write({'warn_text':"",'is_bohui':True})
        current_report.signal_workflow('btn_reject')

class ReportApproveWizard(models.TransientModel):
    _name = 'dtdream.report.approve.wizard'

    liyou = fields.Text("意见")
    if_gongkan = fields.Selection([
        ('1','已工勘'),
        ('0','未工勘'),
    ],string="是否已工勘")
    gongkan_content = fields.Text(string="工勘内容")
    if_view_gongkan = fields.Boolean(string="是否显示工勘")

    # @api.onchange('if_gongkan')
    # def _onchange_id_gongkan(self):
    #     if self.if_gongkan == "1" and self.gongkan_content == u"未工勘":
    #         self.gongkan_content = ""

    @api.one
    def btn_confirm(self):
        current_report = self.env['dtdream.sale.business.report'].browse(self._context['active_id'])
        state_name =dict(self.env['dtdream.sale.business.report']._columns['state'].selection)[current_report.state]
        if self.if_gongkan == '1':
            current_report.if_gongkan = '1'
            current_report.gongkan_content = self.gongkan_content
        elif current_report.state == '2':
            current_report.if_gongkan = '0'
            current_report.gongkan_content = "未工勘"
        shenpiren_name = self.env['hr.employee'].search([('login','=',self.env.user.login)]).name
        self.env['report.handle.approve.record'].create({"shenpiren_version":current_report.shenpiren_version,"name":state_name,"result":"通过","shenpiren":shenpiren_name, "liyou":self.liyou,"report_handle_id":self._context['active_id']})
        if len(current_report.shenpiren)>1:
            current_report.write({'shenpiren':[(3,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        elif current_report.state=="2":
            current_report.pro_zongbu_finish = "1"
        elif current_report.state=="6":
            current_report.pro_office_finish = "1"
        current_report.write({'approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        if current_report.state != '2':
            current_report.write({'business_approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        current_report.write({'warn_text':""})
        current_report.signal_workflow('btn_approve')

class ReportSubmitWizard(models.TransientModel):
    _name = 'dtdream.report.submit.wizard'

    display_text = fields.Char(default="提交后项目进入审批流程，且项目信息无法修改。是否确认提交？")

    @api.one
    def btn_confirm(self):

        current_report = self.env['dtdream.sale.business.report'].browse(self._context['active_id'])
        current_report.signal_workflow('btn_submit')