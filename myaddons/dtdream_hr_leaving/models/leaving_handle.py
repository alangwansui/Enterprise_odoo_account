# -*- coding: utf-8 -*-

from openerp import models, fields, api
# 离职办理
class leaving_handle(models.Model):
    _name = 'leaving.handle'
    _inherit = ['mail.thread']

    @api.depends('name')
    def _compute_employee(self):
        for rec in self:
            rec.job_number=rec.name.job_number
            rec.full_name=rec.name.full_name
            rec.entry_day=rec.name.entry_day
            rec.department=rec.name.department_id.complete_name

    @api.depends("leaving_handle_process_ids1")
    def _compute_process_ids1(self):
        for process in self.leaving_handle_process_ids1:
            if not (process.is_finish or process.is_other) :
                self.is_finish1 = False
                return
        self.is_finish1 = True

    @api.depends("leaving_handle_process_ids2")
    def _compute_process_ids2(self):
        for process in self.leaving_handle_process_ids2:
            if not (process.is_finish or process.is_other) :
                self.is_finish2 = False
                return
        self.is_finish2 = True


    state_list = [('-1','驳回'),('0','离职办理申请'),('1','离职办理确认'),('2','工作交接确认'),('3','离岗前环节'),('4','员工离岗确认'),('5','离岗后环节'),('6','离职手续办理完毕确认'),('7','启动离职结算'),('99','审批完')]
    state_dict = dict(state_list)

    name = fields.Many2one("hr.employee",string="花名",required=True)
    full_name = fields.Char(compute=_compute_employee,string="姓名")
    job_number = fields.Char(compute=_compute_employee,string="工号")
    post = fields.Char(string="岗位")
    entry_day = fields.Date(compute=_compute_employee,string="入职日期")
    department = fields.Char(compute=_compute_employee,string="部门")
    leave_date = fields.Date("计划离职日期")
    actual_leavig_date = fields.Date(string="实际离岗日期")
    opinion_ids = fields.One2many("leaving.handle.wizard","leaving_handle_id",string="审批结果")
    leaving_handle_process_ids1 = fields.One2many("leaving.handle.process","leaving_handle_id1",string="离岗前并行环节")
    leaving_handle_process_ids2 = fields.One2many("leaving.handle.process","leaving_handle_id2",string="离岗后并行环节")
    state = fields.Selection(state_list, default="0",string="离职状态")
    is_finish1 = fields.Boolean(string="离岗前并且环节是否都通过",compute=_compute_process_ids1)
    is_finish2 = fields.Boolean(string="离岗后并且环节是否都通过",compute=_compute_process_ids2)

    @api.multi
    def wkf_draft(self):
        temp1 = self.env['leaving.handle.process'].search([('leaving_handle_id1','=',self.id)])
        temp2 = self.env['leaving.handle.process'].search([('leaving_handle_id2','=',self.id)])
        if len(temp1)+len(temp2) == 0:
            records1 = self.env['process.process'].search([('parent_process','=','3')])
            for record in records1:
                self.env['leaving.handle.process'].create({"process_id":record.id, "leaving_handle_id1":self.id})
            records2 = self.env['process.process'].search([('parent_process','=','5')])
            for record in records2:
                self.env['leaving.handle.process'].create({"process_id":record.id, "leaving_handle_id2":self.id})


        self.write({"state":"0"})

    @api.multi
    def wkf_approve1(self):
        self.write({"state":"1"})

    @api.multi
    def wkf_approve2(self):
        self.write({"state":"2"})

    @api.multi
    def wkf_approve3(self):
        self.write({"state":"3"})

    @api.multi
    def wkf_approve4(self):
        self.write({"state":"4"})

    @api.multi
    def wkf_approve5(self):
        self.write({"state":"5"})

    @api.multi
    def wkf_approve6(self):
        self.write({"state":"6"})

    @api.multi
    def wkf_approve7(self):
        self.write({"state":"7"})

    @api.multi
    def wkf_done(self):
        self.write({"state":"99"})

    @api.multi
    def wkf_reject(self):
        self.write({"state":"-1"})
#审批环节
class leaving_handle_process(models.Model):
    _name = "leaving.handle.process"

    def _compute_process_approver(self):
        for rec in self:
            rec.process_approver = rec.process_id.approver.name

    name = fields.Char("名称")
    is_finish = fields.Boolean("办理完成")
    is_other = fields.Boolean("不涉及")
    remark = fields.Char("备注")
    leaving_handle_id1 = fields.Many2one("leaving.handle",string="离职交接申请")
    leaving_handle_id2 = fields.Many2one("leaving.handle",string="离职交接申请")
    process_id = fields.Many2one("process.process",string="环节")
    process_approver = fields.Char(compute=_compute_process_approver,string="办理人")

#环节基础数据
class process_process(models.Model):
    _name = "process.process"

    name = fields.Char("名称")
    parent_process = fields.Selection([('3','离岗前环节'),('5','离岗后环节')],string="所属环节")
    approver = fields.Many2one("hr.employee",string="审批人")
    handle_process_ids = fields.One2many("leaving.handle.process","process_id",string="环节")






