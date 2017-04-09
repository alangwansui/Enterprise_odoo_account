# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp .exceptions import ValidationError
from datetime import datetime


class dtdream_authorization_submit_wizard(models.TransientModel):
    _name = 'dtdream.authorization.submit.wizard'

    display_text = fields.Char(default="请确认是否为公司标准模板?")

    @api.one
    def btn_normal(self):

        project_authorization = self.env['dtdream.project.bid.authorize.apply'].browse(self._context['active_id'])
        project_authorization.write({"is_normal":True})
        project_authorization.signal_workflow('btn_approve')
        pass

    @api.one
    def btn_not_normal(self):

        project_authorization = self.env['dtdream.project.bid.authorize.apply'].browse(self._context['active_id'])
        project_authorization.write({"is_normal": False})
        project_authorization.signal_workflow('btn_approve')
        # current_report.signal_workflow('btn_submit')
        pass



class dtdream_shenpi_submit_wizard(models.TransientModel):
    _name = 'dtdream.shenpi.submit.wizard'
    shenpi_text = fields.Char(required=True,string="审批意见")

    @api.one
    def btn_reject001(self):
        statedic = {"0":"申请","1":"办事处/系统部审批","2":"规范性审核","3":"审批同意","5":"服务部审批"}
        project_authorization = self.env['dtdream.project.bid.authorize.apply'].browse(self._context['active_id'])
        res = u'驳回' if project_authorization.state != '2' else u'售后服务函非标'
        shenpidic = {"shenpiren": project_authorization.shenpiren.id if project_authorization.shenpiren else None,
                     "time": datetime.now(),
                     "content": self.shenpi_text, "shenpi_text_id": project_authorization.id,"state": statedic.get(project_authorization.state," "),'res':res}
        project_authorization.env["dtdream.shenpi.text"].create(shenpidic)
        project_authorization.signal_workflow('btn_reject')

class dtdream_approval_submit_wizard(models.TransientModel):
    _name = 'dtdream.approval.submit.wizard'
    shenpi_text = fields.Char(default="", string="审批意见")


    @api.one
    def btn_confirm(self):
        statedic = {"0": "申请", "1": "办事处/系统部审批", "2": "规范性审核", "3": "审批同意", "5": "服务部审批"}
        project_authorization = self.env['dtdream.project.bid.authorize.apply'].browse(self._context['active_id'])
        res=u'通过' if project_authorization.state !='2' else u'公司标准模板'
        shenpidic = {"shenpiren": project_authorization.shenpiren.id if project_authorization.shenpiren else None,
                     "time": datetime.now(),
                     "content": self.shenpi_text, "shenpi_text_id": project_authorization.id,"state": statedic.get(project_authorization.state," "),'res':res}
        project_authorization.env["dtdream.shenpi.text"].create(shenpidic)
        project_authorization.signal_workflow('btn_approve')
