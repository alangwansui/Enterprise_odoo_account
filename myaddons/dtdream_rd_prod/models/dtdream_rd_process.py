# -*- coding: utf-8 -*-
from openerp import models, fields, api

#产品审批意见
class dtdream_rd_process(models.Model):
    _name = 'dtdream_rd_process'
    pro_state = fields.Selection([('state_01','立项'),('state_02','总体设计')],string='阶段', readonly=True)
    role = fields.Many2one('dtdream_rd_config',string="角色",readonly=True)
    approver = fields.Many2one('hr.employee',string="审批人",help="可选择进行授权")
    level = fields.Selection([('level_01','一级'),('level_02','二级')],string='级别',readonly=True)
    approver_old = fields.Many2one('hr.employee',string="审批人")


    @api.onchange("is_pass")
    def is_pass_change(self):
        for rec in self:
            if rec.is_pass and rec.is_refuse or rec.is_pass and rec.is_risk:
                rec.is_refuse = False
                rec.is_risk = False

    @api.onchange("is_refuse")
    def is_refuse_change(self):
        for rec in self:
            if rec.is_pass and rec.is_refuse or rec.is_refuse and rec.is_risk:
                rec.is_risk = False
                rec.is_pass = False

    @api.onchange("is_risk")
    def is_risk_change(self):
        for rec in self:
            if rec.is_pass and rec.is_risk or rec.is_refuse and rec.is_risk:
                rec.is_refuse = False
                rec.is_pass = False

    is_pass = fields.Boolean("通过")
    is_refuse = fields.Boolean("不通过")
    is_risk = fields.Boolean("带风险通过")
    approve_state = fields.Text('状态')
    reason = fields.Text("意见")

    process_id = fields.Many2one('dtdream_prod_appr',string='研发产品')
    ztsj_process_id = fields.Many2one('dtdream_prod_appr',string='研发产品')

    is_new = fields.Boolean(string="标记是否为新",default=True)

    @api.model
    def _compute_editable(self):
        for rec in self:
            if rec.pro_state=='state_01':
                if rec.level=='level_01':
                    if rec.process_id.state==rec.pro_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new and not rec.process_id.is_finsished_01:
                        rec.editable=True
                    else:
                        rec.editable=False
                if rec.level=='level_02':
                    if rec.process_id.state==rec.pro_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new:
                        rec.editable=True
                    else:
                        rec.editable=False
            else:
                if rec.level=='level_01':
                    if rec.ztsj_process_id.state==rec.pro_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new and not rec.ztsj_process_id.is_finsished_02:
                        rec.editable=True
                    else:
                        rec.editable=False
                if rec.level=='level_02':
                    if rec.ztsj_process_id.state==rec.pro_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new:
                        rec.editable=True
                    else:
                        rec.editable=False


    editable = fields.Boolean(string="能否修改",compute = _compute_editable,default=True)

    @api.one
    def _compute_is_Qa(self):
        users =  self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users
        ids = []
        for user in users:
            ids+=[user.id]
            for rec in self:
                if self.env.user.id in ids:
                    rec.is_Qa = True
                else:
                    rec.is_Qa=False
    is_Qa = fields.Boolean(string="是否在QA组",compute=_compute_is_Qa,readonly=True)