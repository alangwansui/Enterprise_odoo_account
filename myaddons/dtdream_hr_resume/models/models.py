# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime
from lxml import etree


class dtdream_hr_resume(models.Model):
    _name = "dtdream.hr.resume"
    _description = u"员工详细信息"
    _inherit = ['mail.thread']

    @api.depends('name')
    def _compute_workid_department(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id.complete_name
            rec.is_graduate = rec.name.graduate

    @api.constrains("experince")
    def check_start_end_time(self):
        start = ""
        end = ""
        for index, experince in enumerate(self.experince):
            if index == 0:
                start = experince.start_time
                end = experince.end_time
            else:
                if not(experince.start_time > end or experince.end_time < start):
                    raise ValidationError("工作经历时间填写不合理,时间段之间存在重合!")

    # @api.constrains("degree")
    # def check_entry_leave_time(self):
    #     start = ""
    #     end = ""
    #     if not len(self.degree):
    #         raise ValidationError("至少填写一条学历信息!")
    #     for index, degree in enumerate(self.degree):
    #         if index == 0:
    #             start = degree.entry_time
    #             end = degree.leave_time
    #         else:
    #             if not(degree.entry_time > end or degree.leave_time < start):
    #                 raise ValidationError("学历信息时间填写不合理,时间段之间存在重合!")

    def _compute_has_edit_resume(self):
        if self.name.user_id == self.env.user and self.state == '0':
            self.has_edit = True
        elif (self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id) and self.state == "99":
            self.has_edit = True
        else:
            self.has_edit = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        cr = self.env["dtdream.hr.resume"].search([("name.id", "=", self.env.context.get('active_id'))])
        res = super(dtdream_hr_resume, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        if res['type'] == "form":
            if len(cr):
                doc = etree.XML(res['arch'])
                doc.xpath("//form")[0].set("create", "false")
                res['arch'] = etree.tostring(doc)
        return res

    def _compute_total_work(self):
        total = 0
        for rec in self.experince:
            total += rec.age_work
            self.total_work = total

    def _compute_name_equal_login(self):
        if self.env.user == self.name.user_id:
            self.is_login = True
        else:
            self.is_login = False

    def _compute_is_current(self):
        for rec in self:
            if rec.resume_approve and rec.resume_approve.user_id == rec.env.user:
                rec.is_current = True
            else:
                rec.is_current = False

    def _compute_is_shenqingren(self):
        for rec in self:
            if rec.name.user_id == rec.env.user:
                rec.is_shenqingren = True
            else:
                rec.is_shenqingren = False

    name = fields.Many2one("hr.employee", string="花名", default=lambda self: self.env['hr.employee'].search(
        [("id", "=", self.env.context.get('active_id'))]), readonly="True")
    is_graduate = fields.Boolean(string="是应届毕业生")
    marry = fields.Selection([("0", "未婚"), ("1", "已婚"), ("2", "离异")], string="婚姻", required=True)
    child = fields.Integer(string="子女数")
    icard = fields.Char(string="身份证", required=True)
    mobile = fields.Char(string="手机号", required=True)
    home_address = fields.Char(string="居住地址", required=True)
    is_login = fields.Boolean(string="登入", compute=_compute_name_equal_login)
    workid = fields.Char(string="工号", compute=_compute_workid_department)
    department = fields.Char(string="部门", compute=_compute_workid_department)
    has_title = fields.Boolean(string="是否有职称信息", default=True)
    experince = fields.One2many("hr.employee.experience", "resume", "工作经历")
    total_work = fields.Float(string="合计工龄", compute=_compute_total_work)
    title = fields.One2many("hr.employee.title", "resume", "职称信息")
    degree = fields.One2many("hr.employee.degree", "resume", "学历信息")
    language = fields.One2many("hr.employee.language", "resume", "外语信息")
    has_edit = fields.Boolean(string="是否有编辑权限", compute=_compute_has_edit_resume, default=True)
    resume_approve = fields.Many2one('hr.employee', string="当前审批人")
    is_current = fields.Boolean(string="是否当前审批人", compute=_compute_is_current)
    is_shenqingren = fields.Boolean(string="是否申请人", compute=_compute_is_shenqingren)
    approved = fields.Many2many("hr.employee", string="已批准的审批人")
    state = fields.Selection(
        [("0", "草稿"),
         ("1", "人力资源部审批"),
         ("99", "完成"),
         ("-1", "驳回")], string="状态", default="0")

    @api.multi
    def wkf_draft(self):
        self.write({'state': '0', 'resume_approve': ''})

    @api.multi
    def wkf_approve(self):
        approve = self.env["hr.resume.approve"].search([], limit=1).approve
        self.write({'state': '1', 'resume_approve': approve.id})

    @api.multi
    def wkf_done(self):
        self.write({'state': '99', 'resume_approve': '', "approved": [(4, self.resume_approve.id)]})

    @api.multi
    def wkf_reject(self):
        self.write({'state': '-1', 'resume_approve': '', "approved": [(4, self.resume_approve.id)]})


class dtdream_hr_experience(models.Model):
    _name = "hr.employee.experience"

    @api.depends("start_time", "end_time")
    def _compute_age_work(self):
        time_format = "%Y-%m-%d"
        for rec in self:
            if not rec.end_time or not rec.start_time:
                continue
            rec.age_work = round((datetime.strptime(rec.end_time, time_format) -
                                  datetime.strptime(rec.start_time, time_format)).days / 365.0, 2)

    resume = fields.Many2one("dtdream.hr.resume", "履历")
    start_time = fields.Date(string="开始日期", required=True)
    end_time = fields.Date(string="结束日期", required=True)
    age_work = fields.Float(string="工龄", compute=_compute_age_work)
    company = fields.Char(string="工作单位", required=True)
    post = fields.Char(string="职位", required=True)
    remark = fields.Char(string="备注")

    _sql_constraints = [
        ("date_check", "CHECK(start_time < end_time)", u'结束日期必须大于开始日期')
    ]


class dtdream_hr_title(models.Model):
    _name = "hr.employee.title"

    resume = fields.Many2one("dtdream.hr.resume", "履历")
    resume_modify = fields.Many2one("dtdream.hr.resume.modify", "修改履历")
    name = fields.Char(string="职称名称", required=True)
    depertment = fields.Char(string="授予部门", required=True)
    date = fields.Date(string="授予年月", required=True)
    remark = fields.Char(string="备注")


class dtdream_hr_degree(models.Model):
    _name = "hr.employee.degree"

    resume = fields.Many2one("dtdream.hr.resume", "履历")
    resume_modify = fields.Many2one("dtdream.hr.resume.modify", "修改履历")
    degree = fields.Char(string="专科及以上学历", required=True)
    has_degree = fields.Selection([("0", "是"), ("1", "否")], string="是否获得学位", required=True)
    entry_time = fields.Date(string="在校时间(始)", required=True)
    leave_time = fields.Date(string="在校时间(止)", required=True)
    school = fields.Char(string="学校", required=True)
    major = fields.Char(string="专业", required=True)

    _sql_constraints = [
        ("date_check", "CHECK(entry_time < leave_time)", u'在校时间(止)必须大于在校时间(始)')
    ]


class dtdream_hr_language(models.Model):
    _name = "hr.employee.language"

    resume = fields.Many2one("dtdream.hr.resume", "履历")
    langange = fields.Char(string="外语语种")
    cerdit = fields.Char(string="证书名称")
    result = fields.Char(string="考试结果或分数")
    remark = fields.Char(string="备注")


class dtdream_hr_contract(models.Model):
    _name = "dtdream.hr.contract"

    @api.depends('name')
    def _compute_num_department(self):
        for rec in self:
            rec.num = rec.name.job_number
            rec.department = rec.name.department_id.complete_name

    name = fields.Many2one("hr.employee", string="花名", default=lambda self: self.env['hr.employee'].search(
        [("id", "=", self.env.context.get('active_id'))]))
    num = fields.Char(string="工号", compute=_compute_num_department)
    department = fields.Char(string="部门", compute=_compute_num_department)
    date_start = fields.Date(string="合同开始日期", required=True)
    date_stop = fields.Date(string="合同结束日期", required=True)

    _sql_constraints = [
        ("date_check", "CHECK(date_start < date_stop)", u'合同结束日期必须大于合同开始日期')
    ]


class dtdream_hr_resume_approve(models.Model):
    _name = "hr.resume.approve"

    @api.model
    def create(self, vals):
        cr = self.env["hr.resume.approve"].search([])
        if len(cr):
            raise ValidationError("已经存在一条配置,无法创建多条!")
        return super(dtdream_hr_resume_approve, self).create(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        cr = self.env["hr.resume.approve"].search([])
        res = super(dtdream_hr_resume_approve, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        if res['type'] == "form":
            if cr:
                doc = etree.XML(res['arch'])
                doc.xpath("//form")[0].set("create", "false")
                res['arch'] = etree.tostring(doc)
        return res

    name = fields.Char(default="履历信息人员配置")
    approve = fields.Many2one("hr.employee", string="履历信息审批人")
    remind = fields.Many2many("hr.employee", string="手机号码变更通知人员")


class dtdream_hr_employee(models.Model):
    _inherit = 'hr.employee'

    def _compute_resume_view(self):
        """计算员工是否有权限看到履历按钮"""
        has_view = self.env.ref("dtdream_hr_resume.group_hr_resume_view") in self.env.user.groups_id
        has_edit = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id
        if has_view or has_edit:
            self.resume_view = True
        elif self.user_id == self.env.user:
            self.resume_view = True
        else:
            self.resume_view = False

    def _compute_contract_view(self):
        """计算员工是否有权限看到合同按钮"""
        has_view = self.env.ref("dtdream_hr_resume.group_hr_resume_view") in self.env.user.groups_id
        has_edit = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id
        if has_view or has_edit:
            self.contract_view = True
        elif self.user_id == self.env.user:
            self.contract_view = True
        else:
            self.contract_view = False

    resume_view = fields.Boolean(string="履历是否可见", compute=_compute_resume_view)
    contract_view = fields.Boolean(string="合同是否可见", compute=_compute_contract_view)


class dtdream_resume_modify(models.Model):
    _name = 'dtdream.hr.resume.modify'
    _description = u"修改员工详细信息"
    _inherit = ['mail.thread']

    @api.depends('name')
    def _compute_workid_department(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id.complete_name
            rec.is_graduate = rec.name.graduate

    @api.onchange('child')
    def _check_child_isdigit(self):
        if self.child and not self.child.isdigit():
            self.child = ""
            warning = {
                'title': u'提示',
                'message': u'子女数必须我整数!',
            }
            return {"warning": warning}

    def _compute_is_current(self):
        for rec in self:
            if rec.resume_approve and rec.resume_approve.user_id == rec.env.user:
                rec.is_current = True
            else:
                rec.is_current = False

    def _compute_is_shenqingren(self):
        for rec in self:
            if rec.name.user_id == rec.env.user:
                rec.is_shenqingren = True
            else:
                rec.is_shenqingren = False

    name = fields.Many2one("hr.employee", string="花名", default=lambda self: self.env['hr.employee'].search(
        [("id", "=", self.env.context.get('active_id'))]), readonly="True")
    workid = fields.Char(string="工号", compute=_compute_workid_department)
    department = fields.Char(string="部门", compute=_compute_workid_department)
    marry = fields.Selection([("0", "未婚"), ("1", "已婚"), ("2", "离异")], string="婚姻")
    child = fields.Char(string="子女数")
    icard = fields.Char(string="身份证")
    mobile = fields.Char(string="手机号")
    home_address = fields.Char(string="居住地址")
    title = fields.One2many("hr.employee.title", "resume_modify", "职称信息")
    degree = fields.One2many("hr.employee.degree", "resume_modify", "学历信息")
    infor = fields.Text(string="备注")
    resume_approve = fields.Many2one('hr.employee', string="当前审批人")
    is_current = fields.Boolean(string="是否当前审批人", compute=_compute_is_current)
    is_shenqingren = fields.Boolean(string="是否申请人", compute=_compute_is_shenqingren)
    approved = fields.Many2many("hr.employee", string="已批准的审批人")
    state = fields.Selection(
        [("0", "草稿"),
         ("1", "人力资源部审批"),
         ("99", "完成"),
         ("-1", "驳回")], string="状态", default="0")

    @api.multi
    def wkf_draft(self):
        self.write({'state': '0', 'resume_approve': ''})

    @api.multi
    def wkf_approve(self):
        approve = self.env["hr.resume.approve"].search([], limit=1).approve
        self.write({'state': '1', 'resume_approve': approve.id})

    @api.multi
    def wkf_done(self):
        self.write({'state': '99', 'resume_approve': '', "approved": [(4, self.resume_approve.id)]})

    @api.multi
    def wkf_reject(self):
        self.write({'state': '-1', 'resume_approve': '', "approved": [(4, self.resume_approve.id)]})







