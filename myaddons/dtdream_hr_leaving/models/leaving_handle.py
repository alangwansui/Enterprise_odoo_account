# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
from lxml import etree
# 离职办理
class leaving_handle(models.Model):
    _name = 'leaving.handle'
    _description = u"离职办理"
    #创建单据时，在备注中会显示“离职办理 创建”
    _inherit = ['mail.thread']

    # 根据申请人带出工号、姓名、入职日期、所在部门
    @api.depends('name')
    def _compute_employee(self):
        for rec in self:
            rec.job_number=rec.name.job_number
            rec.full_name=rec.name.full_name
            rec.entry_day=rec.name.entry_day
            rec.department_id=rec.name.department_id
    # 用于判断离岗前环节是否全部批完
    @api.depends("leaving_handle_process_ids1")
    def _compute_process_ids1(self):
        for process in self.leaving_handle_process_ids1:
            if not (process.is_finish or process.is_other) :
                self.is_finish1 = False
                return
        self.is_finish1 = True
    # 用于判断离岗后环节是否全部批完
    @api.depends("leaving_handle_process_ids2")
    def _compute_process_ids2(self):
        for process in self.leaving_handle_process_ids2:
            if not (process.is_finish or process.is_other) :
                self.is_finish2 = False
                return
        self.is_finish2 = True
    # 用于判断当前登录人是否是审批人
    def _compute_cur_approver(self):
        if self.env["hr.employee"].search([("login", "=", self.env.user.login)]) in self.cur_approvers:
            self.is_approver = True
    # 将当前登录人默认作为申请人
    def _default_current_employee(self):
        return self.env["hr.employee"].search([("login","=",self.env.user.login)])
    # 判断用户是否含有离职管理员权限
    @api.depends("name")
    def _compute_is_admin(self):
        self.is_admin = self.user_has_groups('dtdream_hr_leaving.group_dtdream_leaving_admin')
    # 计算是否有审批记录，用于显示审批记录
    @api.depends("opinion_ids")
    def _compute_opinion_count(self):
        self.opinion_count = len(self.opinion_ids)>0

    state_list = [('0',u'草稿'),('1',u'离职办理确认'),('2',u'工作交接确认'),('3',u'离岗前环节'),('4',u'员工离岗确认'),('5',u'离岗后环节'),('6',u'离职手续办理完毕确认'),('7',u'启动离职结算'),('8',u'离职结算支付确认'),('-1',u'驳回'),('99',u'完成')]
    state_dict = dict(state_list)

    name = fields.Many2one("hr.employee",string="申请人",required=True,default=_default_current_employee)
    full_name = fields.Char(compute=_compute_employee,string="姓名")
    job_number = fields.Char(compute=_compute_employee,string="工号")
    post = fields.Char(string="岗位",size=32, required=True)
    entry_day = fields.Date(compute=_compute_employee,string="入职日期")
    department_id = fields.Many2one("hr.department",compute=_compute_employee,store=True,string="部门")
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
    manager_id = fields.Many2one("hr.employee",string="主管")
    assistant_id = fields.Many2one('hr.employee', string="行政助理")
    is_admin = fields.Boolean("是否管理员",compute=_compute_is_admin)
    opinion_count = fields.Boolean("是否有审批记录",compute=_compute_opinion_count)
    # 获取系统配置的邮件发送人
    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user
    # 获取当前系统的网址基础部分
    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    @api.model
    def create(self, vals):
        leaving_handle_ids = self.env["leaving.handle"].search([('name.id', '=', vals["name"])])
        if len(leaving_handle_ids)>0:
            raise osv.except_osv(u'您已经发起离职办理申请，不能重复发起！')
        return super(leaving_handle, self).create(vals)

    @api.multi
    def unlink(self):
        is_admin = self.env.ref("dtdream_hr_leaving.group_dtdream_leaving_admin") in self.env.user.groups_id
        # 判断当前用户是否是离职管理员
        for rec in self:
            if not is_admin and rec.state != '0':
                raise osv.except_osv(u'审批流程中的离职办理不能删除!')
            return super(leaving_handle, self).unlink()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(leaving_handle, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                               submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"我的申请":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
            if res['type'] == "kanban":
                doc.xpath("//kanban")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def wkf_draft(self):
        origin_state = self.state
        self.cur_approvers = False
        self.write({"state": "0"})
        if origin_state == "1":
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=leaving.handle' % self.id
            url = base_url + link
            self.env['mail.mail'].create({
                'body_html': u'<p>您好</p>'
                             u'<p>%s的离职办理已被驳回</p>'
                             u'<p>请点击链接重新提交:'
                             u'<a href="%s">%s</a></p>'
                             u'<p>dodo</p>'
                             u'<p>万千业务，简单有do</p>'
                             u'<p>%s<p>' % (self.name.user_id.name, url, url, self.write_date[:10]),
                'subject': u'您的离职办理已被驳回至“%s”' % (self.state_dict[self.state]),
                'email_to': self.name.work_email,
                'auto_delete': False,
                'email_from': self.get_mail_server_name(),
            }).send()

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
        self.message_post(body=u'状态：'+self.state_dict[origin_state] + '--> ' + self.state_dict[self.state])
        if origin_state == "0":
            self.approver_mail()
        elif origin_state == "2":
            self.reject_mail()


    @api.multi
    def wkf_approve2(self):
        origin_state = self.state
        self.cur_approvers = self.manager_id
        self.write({"state":"2"})
        self.message_post(body=u'状态：' + self.state_dict[origin_state] + '--> ' + self.state_dict[self.state])
        if origin_state == "1":
            self.approver_mail()
        elif origin_state == "3":
            self.reject_mail()

    @api.multi
    def wkf_approve3(self):
        origin_state = self.state
        self.write({"state":"3"})
        self.env['leaving.handle.process'].search([('leaving_handle_id1', '=', self.id)]).unlink()
        records = self.env['process.process'].search([('parent_process', '=', '3')])
        self.message_post(body=u'状态：' + self.state_dict[origin_state] + '--> ' + self.state_dict[self.state])
        for record in records:
            approver = record.approver
            if record.is_assistant:
                approver = self.assistant_id
            self.env['leaving.handle.process'].create({"process_id": record.id,"process_approver":approver.id, "leaving_handle_id1": self.id})
        cur_approver_ids = set([])
        for process in self.leaving_handle_process_ids1:
            if process.process_approver.id:
                cur_approver_ids.add(process.process_approver.id)
        self.cur_approvers = self.env["hr.employee"].browse(cur_approver_ids)
        if origin_state == "2":
            self.approver_mail()
        elif origin_state == "4":
            self.reject_mail()

    @api.multi
    def wkf_approve4(self):
        origin_state = self.state
        self.write({"state":"4"})
        self.cur_approvers = self.manager_id
        self.message_post(body=u'状态：' + self.state_dict[origin_state] + '--> ' + self.state_dict[self.state])
        if origin_state == "3":
            self.approver_mail()
        elif origin_state == "5":
            self.reject_mail()

    @api.multi
    def wkf_approve5(self):
        origin_state = self.state
        self.write({"state":"5"})
        self.env['leaving.handle.process'].search([('leaving_handle_id2', '=', self.id)]).unlink()
        records = self.env['process.process'].search([('parent_process', '=', '5')])
        self.message_post(body=u'状态：' + self.state_dict[origin_state] + '--> ' + self.state_dict[self.state])
        for record in records:
            approver = record.approver
            if record.is_assistant:
                approver = self.assistant_id
            self.env['leaving.handle.process'].create({"process_id": record.id,"process_approver":approver.id, "leaving_handle_id2": self.id})
        cur_approver_ids = set([])
        for process in self.leaving_handle_process_ids2:
            if process.process_approver.id:
                cur_approver_ids.add(process.process_approver.id)
        self.cur_approvers = self.env["hr.employee"].browse(cur_approver_ids)
        if origin_state == "4":
            self.approver_mail()
        elif origin_state == "6":
            self.reject_mail()

    @api.multi
    def wkf_approve6(self):
        origin_state = self.state
        self.write({"state":"6"})
        self.cur_approvers = self.env.ref('dtdream_hr_leaving.leaving_handle_approver_6').approver
        self.message_post(body=u'状态：' + self.state_dict[origin_state] + '--> ' + self.state_dict[self.state])
        if origin_state == "5":
            self.approver_mail()
        elif origin_state == "7":
            self.reject_mail()


    @api.multi
    def wkf_approve7(self):
        origin_state = self.state
        self.write({"state":"7"})
        self.cur_approvers = self.env.ref('dtdream_hr_leaving.leaving_handle_approver_7').approver
        self.message_post(body=u'状态：' + self.state_dict[origin_state] + '--> ' + self.state_dict[self.state])
        if origin_state == "6":
            self.approver_mail()
        elif origin_state == "8":
            self.reject_mail()


    @api.multi
    def wkf_approve8(self):
        origin_state = self.state
        self.write({"state": "8"})
        self.cur_approvers = self.env.ref('dtdream_hr_leaving.leaving_handle_approver_8').approver
        self.message_post(body=u'状态：' + self.state_dict[origin_state] + '--> ' + self.state_dict[self.state])
        if origin_state == "7":
            self.approver_mail()
        elif origin_state == "9":
            self.reject_mail()

    @api.multi
    def wkf_done(self):
        self.cur_approvers = False
        self.message_post(body=u'状态：' + self.state_dict[self.state] + u'--> 完成')
        self.write({"state":"99"})

# 审批记录
class leaving_handle_approve_record(models.Model):
    _name = "leaving.handle.approve.record"

    name = fields.Char("审批环节")
    result = fields.Selection([("agree","同意"),("finish","办理完成"),("reject","驳回到上一步"),("other","不涉及"),("is_finish","办理完成")],string="审批结果")
    opinion = fields.Text("意见", required=True)
    actual_leavig_date = fields.Date("实际离岗时间")
    leaving_handle_id = fields.Many2one("leaving.handle",string="离职交接申请")
    mail_ccs = fields.Many2many('hr.employee',string="抄送人")

#离岗并行环节
class leaving_handle_process(models.Model):
    _name = "leaving.handle.process"

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
    # 用于控制离岗前并行环节审批按钮的显示隐藏控制
    # 处于离岗前环节，并且当前登录人是处理人或管理员才显示审批按钮
    def _if_process1_can_edit(self):
        for rec in self:
            if rec.leaving_handle_id1.state == '3' and (self.env.user == rec.process_approver.user_id or self.user_has_groups('dtdream_hr_leaving.group_dtdream_leaving_admin')):
                rec.process1_can_edit = True
            else:
                rec.process1_can_edit = False
    # 用于控制离岗后并行环节审批按钮的显示隐藏控制
    # 处于离岗后环节，并且当前登录人是处理人或管理员才显示审批按钮
    def _if_process2_can_edit(self):
        for rec in self:
            if rec.leaving_handle_id2.state == '5' and (self.env.user == rec.process_approver.user_id or self.user_has_groups('dtdream_hr_leaving.group_dtdream_leaving_admin')):
                rec.process2_can_edit = True
            else:
                rec.process2_can_edit = False
    # 由于无法解决点击one2many字段不弹窗问题，所以使用隐藏办理完成和不涉及字段，将这些字段拼接到意见上显示
    def _compute_remarks(self):
        for rec in self:
            rec.remarks = ""
            if rec.is_finish:
                rec.remarks += u"办理完成，"
            elif rec.is_other:
                rec.remarks += u"不涉及，"
            if rec.remark:
                rec.remarks += rec.remark

    name = fields.Char("名称")
    is_finish = fields.Boolean("办理完成")
    is_other = fields.Boolean("不涉及")
    remark = fields.Char("意见",size=100)
    remarks = fields.Char("意见",compute=_compute_remarks) #将审批结果拼接起来
    leaving_handle_id1 = fields.Many2one("leaving.handle",string="离职交接申请")
    leaving_handle_id2 = fields.Many2one("leaving.handle",string="离职交接申请")
    process_id = fields.Many2one("process.process",string="环节")
    process_approver = fields.Many2one("hr.employee",string="办理人")
    process1_can_edit= fields.Boolean("是否可以修改",compute=_if_process1_can_edit)
    process2_can_edit= fields.Boolean("是否可以修改",compute=_if_process2_can_edit)

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






