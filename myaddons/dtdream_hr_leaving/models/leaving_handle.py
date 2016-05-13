# -*- coding: utf-8 -*-

from openerp import models, fields, api
# 离职办理
class leaving_handle(models.Model):
    _name = 'leaving.handle'
    _description = u"离职办理"
    _inherit = ['mail.thread']

    @api.depends('name')
    def _compute_employee(self):
        for rec in self:
            rec.job_number=rec.name.job_number
            rec.full_name=rec.name.full_name
            rec.entry_day=rec.name.entry_day
            rec.department_id=rec.name.department_id

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

    def _compute_cur_approver(self):
        if self.env["hr.employee"].search([("login", "=", self.env.user.login)]) in self.cur_approvers:
            self.is_approver = True


    def _default_current_employee(self):
        return self.env["hr.employee"].search([("login","=",self.env.user.login)])

    @api.depends("name")
    def _compute_is_admin(self):
        self.is_admin = self.user_has_groups('dtdream_hr_leaving.group_dtdream_leaving_admin')

    state_list = [('0',u'草稿'),('1',u'离职办理确认'),('2',u'工作交接确认'),('3',u'离岗前环节'),('4',u'员工离岗确认'),('5',u'离岗后环节'),('6',u'离职手续办理完毕确认'),('7',u'启动离职结算'),('8',u'离职结算支付确认'),('-1',u'驳回'),('99',u'完成')]
    state_dict = dict(state_list)

    name = fields.Many2one("hr.employee",string="申请人",required=True,default=_default_current_employee)
    full_name = fields.Char(compute=_compute_employee,string="姓名")
    job_number = fields.Char(compute=_compute_employee,string="工号")
    post = fields.Char(string="岗位", required=True)
    entry_day = fields.Date(compute=_compute_employee,string="入职日期")
    department_id = fields.Many2one("hr.department",compute=_compute_employee,string="部门")
    leave_date = fields.Date("计划离职日期",required=True)
    actual_leavig_date = fields.Date(string="实际离岗日期")
    opinion_ids = fields.One2many("leaving.handle.approve.record","leaving_handle_id",string="审批结果")
    leaving_handle_process_ids1 = fields.One2many("leaving.handle.process","leaving_handle_id1",string="离岗前并行环节")
    leaving_handle_process_ids2 = fields.One2many("leaving.handle.process","leaving_handle_id2",string="离岗后并行环节")
    state = fields.Selection(state_list, default="0",string="离职状态")
    is_finish1 = fields.Boolean(string="离岗前并且环节是否都通过",compute=_compute_process_ids1)
    is_finish2 = fields.Boolean(string="离岗后并且环节是否都通过",compute=_compute_process_ids2)
    is_approver = fields.Boolean(string="判断当前登录人是否是该环节的审批人",compute=_compute_cur_approver)
    cur_approvers = fields.Many2many("hr.employee",string="当前处理人")
    cur_approver_users = fields.Many2many("res.users",string="当前处理人")
    manager_id = fields.Many2one("hr.employee",string="主管")
    assistant_id = fields.Many2one('hr.employee', string="行政助理")
    is_admin = fields.Boolean("是否管理员",compute=_compute_is_admin)

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    @api.multi
    def multi_process_btn_submit(self):
        self.signal_workflow("btn_submit")

    @api.multi
    def wkf_draft(self):
        self.cur_approvers = False
        self.cur_approver_users = False
        self.write({"state": "0"})

    # 审批时发送的邮件
    def approver_mail(self):
        subject = u'%s的离职办理已经进入“%s”，请您审批' % (self.name.user_id.name, self.state_dict[self.state])
        email_to = "";
        for employee in self.cur_approvers:
            email_to += employee.work_email+";"
        if email_to:
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=leaving.handle' % self.id
            url = base_url + link

            self.env['mail.mail'].create({
                'body_html': u'<p>您好</p>'
                             u'<p>%s的离职办理等待您的审批</p>'
                             u'<p>请点击链接进入审批:'
                             u'<a href="%s">%s</a></p>'
                             u'<p>dodo</p>'
                             u'<p>万千业务，简单有do</p>'
                             u'<p>%s<p>' % (self.name.user_id.name, url, url, self.write_date[:10]),
                'subject': subject,
                'email_to': email_to,
                'auto_delete': False,
                'email_from': self.get_mail_server_name(),
            }).send()

    # 驳回到上一步时发送的邮件
    def reject_mail(self):
        subject = u'%s的离职办理被驳回至“%s”，请您审批' % (self.name.user_id.name, self.state_dict[self.state])
        email_to = "";
        for employee in self.cur_approvers:
            email_to += employee.work_email + ";"
        if email_to:
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=leaving.handle' % self.id
            url = base_url + link

            self.env['mail.mail'].create({
                'body_html': u'<p>您好</p>'
                             u'<p>%s的离职办理等待您的审批</p>'
                             u'<p>请点击链接进入审批:'
                             u'<a href="%s">%s</a></p>'
                             u'<p>dodo</p>'
                             u'<p>万千业务，简单有do</p>'
                             u'<p>%s<p>' % (self.name.user_id.name, url, url, self.write_date[:10]),
                'subject': subject,
                'email_to': email_to,
                'auto_delete': False,
                'email_from': self.get_mail_server_name(),
            }).send()

    @api.multi
    def wkf_approve1(self):
        origin_state = self.state
        self.write({"state":"1"})
        self.cur_approvers = self.env.ref('dtdream_hr_leaving.leaving_handle_approver_1').approver
        user_ids = []
        for approver in self.cur_approvers:
            user_ids.append(approver.user_id.id)
        self.cur_approver_users = self.env["res.users"].browse(user_ids)
        if origin_state == "0":
            self.approver_mail()
        elif origin_state == "2":
            self.reject_mail()


    @api.multi
    def wkf_approve2(self):
        origin_state = self.state
        self.cur_approvers = self.manager_id
        user_ids = []
        for approver in self.cur_approvers:
            user_ids.append(approver.user_id.id)
        self.cur_approver_users = self.env["res.users"].browse(user_ids)
        self.write({"state":"2"})
        if origin_state == "1":
            self.approver_mail()
        elif origin_state == "3":
            self.reject_mail()

    @api.multi
    def wkf_approve3(self):
        origin_state = self.state
        self.write({"state":"3"})
        if origin_state == "2":
            self.env['leaving.handle.process'].search([('leaving_handle_id1', '=', self.id)]).unlink()
            records = self.env['process.process'].search([('parent_process', '=', '3')])
            for record in records:
                self.env['leaving.handle.process'].create({"process_id": record.id, "leaving_handle_id1": self.id})
            cur_approver_ids = set([])
            for process in self.leaving_handle_process_ids1:
                if process.process_approver.id:
                    cur_approver_ids.add(process.process_approver.id)
            self.cur_approvers = self.env["hr.employee"].browse(cur_approver_ids)
            user_ids = []
            for approver in self.cur_approvers:
                user_ids.append(approver.user_id.id)
            self.cur_approver_users = self.env["res.users"].browse(user_ids)
            self.approver_mail()
        elif origin_state == "4":
            self.reject_mail()

    @api.multi
    def wkf_approve4(self):
        origin_state = self.state
        self.write({"state":"4"})
        self.cur_approvers = self.manager_id
        user_ids = []
        for approver in self.cur_approvers:
            user_ids.append(approver.user_id.id)
        self.cur_approver_users = self.env["res.users"].browse(user_ids)
        if origin_state == "3":
            self.approver_mail()
        elif origin_state == "5":
            self.reject_mail()

    @api.multi
    def wkf_approve5(self):
        origin_state = self.state
        self.write({"state":"5"})
        if origin_state == "4":
            self.env['leaving.handle.process'].search([('leaving_handle_id2', '=', self.id)]).unlink()
            records = self.env['process.process'].search([('parent_process', '=', '5')])
            for record in records:
                self.env['leaving.handle.process'].create({"process_id": record.id, "leaving_handle_id2": self.id})
            cur_approver_ids = set([])
            for process in self.leaving_handle_process_ids2:
                if process.process_approver.id:
                    cur_approver_ids.add(process.process_approver.id)
            self.cur_approvers = self.env["hr.employee"].browse(cur_approver_ids)
            user_ids = []
            for approver in self.cur_approvers:
                user_ids.append(approver.user_id.id)
            self.cur_approver_users = self.env["res.users"].browse(user_ids)
            self.approver_mail()
        elif origin_state == "6":
            self.reject_mail()


    @api.multi
    def wkf_approve6(self):
        origin_state = self.state
        self.write({"state":"6"})
        self.cur_approvers = self.env.ref('dtdream_hr_leaving.leaving_handle_approver_6').approver
        user_ids = []
        for approver in self.cur_approvers:
            user_ids.append(approver.user_id.id)
        self.cur_approver_users = self.env["res.users"].browse(user_ids)
        if origin_state == "5":
            self.approver_mail()
        elif origin_state == "7":
            self.reject_mail()


    @api.multi
    def wkf_approve7(self):
        origin_state = self.state
        self.write({"state":"7"})
        self.cur_approvers = self.env.ref('dtdream_hr_leaving.leaving_handle_approver_7').approver
        user_ids = []
        for approver in self.cur_approvers:
            user_ids.append(approver.user_id.id)
        self.cur_approver_users = self.env["res.users"].browse(user_ids)
        if origin_state == "6":
            self.approver_mail()
        elif origin_state == "8":
            self.reject_mail()


    @api.multi
    def wkf_approve8(self):
        origin_state = self.state
        self.write({"state": "8"})
        self.cur_approvers = self.env.ref('dtdream_hr_leaving.leaving_handle_approver_8').approver
        user_ids = []
        for approver in self.cur_approvers:
            user_ids.append(approver.user_id.id)
        self.cur_approver_users = self.env["res.users"].browse(user_ids)
        if origin_state == "7":
            self.approver_mail()
        elif origin_state == "9":
            self.reject_mail()

    @api.multi
    def wkf_done(self):
        self.cur_approvers = False
        self.cur_approver_users = False
        self.write({"state":"99"})

# 审批记录
class leaving_handle_approve_record(models.Model):
    _name = "leaving.handle.approve.record"

    name = fields.Char("审批环节")
    result = fields.Selection([("agree","同意"),("reject","驳回到上一步"),("other","不涉及")],string="审批结果")
    opinion = fields.Text("意见", required=True)
    actual_leavig_date = fields.Date("实际离岗时间")
    leaving_handle_id = fields.Many2one("leaving.handle",string="离职交接申请")
    mail_ccs = fields.Many2many('hr.employee',string="抄送人")

#离岗并行环节
class leaving_handle_process(models.Model):
    _name = "leaving.handle.process"

    def _compute_process_approver(self):
        for rec in self:
            rec.process_approver = rec.process_id.approver
            if rec.process_id.code == "101":
                rec.process_approver = rec.leaving_handle_id1.assistant_id
            if rec.process_id.code == "201":
                rec.process_approver = rec.leaving_handle_id2.assistant_id


    @api.onchange("is_finish")
    def is_finish_change(self):
        for rec in self:
            if rec.is_finish and rec.is_other:
                rec.is_other = False

    @api.onchange("is_other")
    def is_other_change(self):
        for rec in self:
            if rec.is_other and rec.is_finish:
                rec.is_finish = False

    def _if_process_can_edit(self):
        for rec in self:
            if self.env.user == rec.process_approver.user_id:
                rec.can_edit = True
            else:
                rec.can_edit = False

    name = fields.Char("名称")
    is_finish = fields.Boolean("办理完成")
    is_other = fields.Boolean("不涉及")
    remark = fields.Char("备注")
    leaving_handle_id1 = fields.Many2one("leaving.handle",string="离职交接申请")
    leaving_handle_id2 = fields.Many2one("leaving.handle",string="离职交接申请")
    process_id = fields.Many2one("process.process",string="环节")
    process_approver = fields.Many2one("hr.employee",compute=_compute_process_approver,string="办理人")
    can_edit = fields.Boolean("是否可以修改",compute=_if_process_can_edit)

#并行环节基础数据
class process_process(models.Model):
    _name = "process.process"

    name = fields.Char("名称")
    code = fields.Char("环节编码")
    parent_process = fields.Selection([('3','离岗前环节'),('5','离岗后环节')],string="所属环节")
    approver = fields.Many2one("hr.employee",string="审批人")
    is_assistant = fields.Boolean("是否行政助理审批")

#离职交接办理环节审批人配置
class leaving_handle_approver(models.Model):
    _name="leaving.handle.approver"
    name = fields.Char("环节名称")
    approver = fields.Many2many("hr.employee",string="审批人")






