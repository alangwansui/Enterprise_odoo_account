# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime


class dtdream_hr_resume(models.Model):
    _name = "dtdream.hr.resume"
    _description = u"员工详细信息"
    _inherit = ['mail.thread']

    @api.depends('name')
    def _compute_workid_department(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id.complete_name

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

    @api.constrains("degree")
    def check_entry_leave_time(self):
        start = ""
        end = ""
        if not len(self.degree):
            raise ValidationError("至少填写一条学历信息!")
        for index, degree in enumerate(self.degree):
            if index == 0:
                start = degree.entry_time
                end = degree.leave_time
            else:
                if not(degree.entry_time > end or degree.leave_time < start):
                    raise ValidationError("学历信息时间填写不合理,时间段之间存在重合!")

    @api.depends("experince")
    def _compute_total_work(self):
        total = 0
        for rec in self.experince:
            total += rec.age_work
            self.total_work = total

    name = fields.Many2one("hr.employee", string="花名", default=lambda self: self.env['hr.employee'].search(
        [("id", "=", self.env.context.get('active_id'))]), readonly="True")
    is_graduate = fields.Boolean(related="name.graduate", string="是应届毕业生")
    workid = fields.Char(string="工号", compute=_compute_workid_department)
    department = fields.Char(string="部门", compute=_compute_workid_department)
    has_title = fields.Boolean(string="是否有职称信息", default=True)
    experince = fields.One2many("hr.employee.experience", "resume", "工作经历")
    total_work = fields.Float(string="合计工龄", compute=_compute_total_work)
    title = fields.One2many("hr.employee.title", "resume", "职称信息")
    degree = fields.One2many("hr.employee.degree", "resume", "学历信息")
    language = fields.One2many("hr.employee.language", "resume", "外语信息")
    state = fields.Selection(
        [("0", "草稿"),
         ("1", "人力资源部审批"),
         ("99", "完成"),
         ("-1", "驳回")], string="状态", default="0")

    @api.multi
    def wkf_draft(self):
        self.write({'state': '0'})

    @api.multi
    def wkf_approve(self):
        self.write({'state': '1'})

    @api.multi
    def wkf_done(self):
        self.write({'state': '99'})

    @api.multi
    def wkf_reject(self):
        self.write({'state': '-1'})


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
    name = fields.Char(string="职称名称", required=True)
    depertment = fields.Char(string="授予部门", required=True)
    date = fields.Date(string="授予年月", required=True)
    remark = fields.Char(string="备注")


class dtdream_hr_degree(models.Model):
    _name = "hr.employee.degree"

    resume = fields.Many2one("dtdream.hr.resume", "履历")
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


class dtdream_hr_resume_approve(models.Model):
    _name = "hr.resume.approve"

    name = fields.Char(default="履历信息审批人")
    approve = fields.Many2many("hr.employee", string="履历信息审批人")


class dtdream_hr_remind_mobile(models.Model):
    _name = "hr.remind.mobile"

    name = fields.Char(default="手机号码变更通知人员配置")
    remind = fields.Many2many("hr.employee", string="手机号码变更通知人员")


class dtdream_hr_employee(models.Model):
    _inherit = 'hr.employee'

    resume = fields.One2many("dtdream.hr.resume", "name", string="履历")






