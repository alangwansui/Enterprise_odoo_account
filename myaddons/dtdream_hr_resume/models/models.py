# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime
from lxml import etree


class dtdream_hr_resume(models.Model):
    _name = "dtdream.hr.resume"
    _description = u"员工履历"
    _inherit = ['mail.thread']

    @api.depends('name')
    def _compute_workid_department(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id.complete_name
            rec.is_graduate = rec.name.graduate

    @api.constrains("experince")
    def check_start_end_time(self):
        for index, experince in enumerate(self.experince):
            start = experince.start_time
            end = experince.end_time
            for j in range(index):
                if not(self.experince[j].start_time > end or self.experince[j].end_time < start):
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
        view = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") not in self.env.user.groups_id
        user_id = self._context.get('active_id', None)
        res = super(dtdream_hr_resume, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        if res['type'] == "form":
            doc = etree.XML(res['arch'])
            if len(cr) or not user_id:
                doc.xpath("//form")[0].set("create", "false")
                if view:
                    doc.xpath("//form")[0].set("edit", "false")
            res['arch'] = etree.tostring(doc)
        if res['type'] == "tree":
            if not user_id:
                doc = etree.XML(res['arch'])
                doc.xpath("//tree")[0].set("create", "false")
                if view:
                    doc.xpath("//tree")[0].set("edit", "false")
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

    @api.multi
    def act_dtdream_hr_resume_modify(self):
        """create one new record which is the same as the resume when click the resume_modify button"""
        cr = self.env["dtdream.hr.resume.modify"].create({"name": self.name.id, "is_graduate": self.is_graduate,
                                                          "workid": self.workid, "department": self.department,
                                                          "has_title": self.title, "marry": self.marry,
                                                          "child": self.child, "icard": self.icard, "state": '0',
                                                          "mobile": self.mobile, "home_address": self.home_address})
        res_id = cr.id
        for ex in self.experince:
            self.env["hr.employee.experience"].create({"start_time": ex.start_time, "end_time": ex.end_time,
                                                       "resume_modify": res_id, "company": ex.company,
                                                       "post": ex.post, "remark": ex.remark, "related": ex.id})
        for ex in self.title:
            self.env["hr.employee.title"].create({"name": ex.name, "depertment": ex.depertment,
                                                  "resume_modify": res_id, "date": ex.date,
                                                  "remark": ex.remark, "related": ex.id})
        for ex in self.degree:
            self.env["hr.employee.degree"].create({"degree": ex.degree, "has_degree": ex.has_degree,
                                                  "resume_modify": res_id, "entry_time": ex.entry_time,
                                                   "leave_time": ex.leave_time, "school": ex.school,
                                                   "major": ex.major, "related": ex.id})
        for ex in self.language:
            self.env["hr.employee.language"].create({"langange": ex.langange, "cerdit": ex.cerdit, "related": ex.id,
                                                     "resume_modify": res_id, "result": ex.result, "remark": ex.remark})
        action = {
                'name': '员工履历',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'dtdream.hr.resume.modify',
                'res_id': res_id,
                'context': self._context,
                }
        return action

    @api.constrains('title')
    def constrains_title_record(self):
        if self.has_title and not len(self.title):
            raise ValidationError("请至少填写一条职称信息!")

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_mail_attend_mobile(self, email):
        email_to = email.work_email
        appellation = u'{0},您好：'.format(email.full_name)
        subject = u"手机号码变更通知"
        content = u"%s,员工手机号更改为%s,请您知悉!" % (self.name.full_name, self.mobile)
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    def send_mail_attend_resume(self, name, subject, content):
        email_to = name.work_email
        appellation = u'{0},您好：'.format(name.full_name)
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    def update_mobile_number(self):
        self.env['hr.employee'].search([('id', '=', self.name.id)]).write({"mobile_phone": self.mobile})
        cr = self.env["hr.resume.approve"].search([])
        if cr.email:
            self.send_mail_attend_mobile(cr.email)
        if cr.weixin:
            self.send_mail_attend_mobile(cr.weixin)
        if cr.dingding:
            self.send_mail_attend_mobile(cr.dingding)
        if cr.cloud:
            self.send_mail_attend_mobile(cr.cloud)
        if cr.oa:
            self.send_mail_attend_mobile(cr.cloud)

    @api.model
    def create(self, vals):
        cr = self.env["dtdream.hr.resume"].search([('name.id', '=', self._context.get("active_id"))])
        if len(cr):
            raise ValidationError("履历信息已经存在,无法重复创建!")
        return super(dtdream_hr_resume, self).create(vals)

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
        self.send_mail_attend_resume(approve, subject=u'%s提交了员工履历信息,请您审批!' % self.name.name,
                                     content=u"%s提交了员工履历信息,等待您的审批!" % self.name.full_name)
        self.write({'state': '1', 'resume_approve': approve.id})

    @api.multi
    def wkf_done(self):
        self.update_mobile_number()
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
    resume_modify = fields.Many2one("dtdream.hr.resume.modify", "修改履历")
    related = fields.Integer(string="related")
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
    related = fields.Integer(string="related")
    name = fields.Char(string="职称名称", required=True)
    depertment = fields.Char(string="授予部门", required=True)
    date = fields.Date(string="授予年月", required=True)
    remark = fields.Char(string="备注")


class dtdream_hr_degree(models.Model):
    _name = "hr.employee.degree"

    resume = fields.Many2one("dtdream.hr.resume", "履历")
    resume_modify = fields.Many2one("dtdream.hr.resume.modify", "修改履历")
    related = fields.Integer(string="related")
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
    resume_modify = fields.Many2one("dtdream.hr.resume.modify", "修改履历")
    related = fields.Integer(string="related")
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

    @api.constrains("approve")
    def write_approve_to_resume(self):
        self.env['dtdream.hr.resume'].search([('state', '=', '1')]).write({'resume_approve': self.approve.id})
        self.env['dtdream.hr.resume.modify'].search([('state', '=', '1')]).write({'resume_approve': self.approve.id})

    name = fields.Char(default="员工入职相关配置")
    approve = fields.Many2one("hr.employee", string="履历信息审批人", required=True)
    account = fields.Many2one("hr.employee", string="域帐号管理员", required=True)
    email = fields.Many2one('hr.employee', string='邮箱管理员', required=True)
    weixin = fields.Many2one('hr.employee', string='微信管理员', required=True)
    dingding = fields.Many2one('hr.employee', string='钉钉管理员', required=True)
    cloud = fields.Many2one('hr.employee', string='云学堂管理员', required=True)
    bbs = fields.Many2one('hr.employee', string='BBS管理员', required=True)
    oa = fields.Many2one('hr.employee', string='OA管理员', required=True)
    dodo = fields.Many2one('hr.employee', string='dodo管理员', required=True)


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

    @api.multi
    def act_dtdream_hr_resume(self):
        cr = self.env['dtdream.hr.resume'].search([('name.id', '=', self.id)])
        res_id = cr.id if cr else ''
        if not cr and self.env.user != self.user_id:
            raise ValidationError("该员工还未创建履历信息,暂时无法查看!")
        action = {
            'name': '员工履历',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dtdream.hr.resume',
            'res_id': res_id,
            'context': self._context,
            }
        return action

    def _compute_resume_log(self):
        cr = self.env['dtdream.hr.resume'].search([("name.id", "=", self.id)])
        self.resume_log_nums = len(cr)

    def _compute_contract_log(self):
        cr = self.env['dtdream.hr.contract'].search([("name.id", "=", self.id)])
        self.contract_log_nums = len(cr)

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_mail_remind_open_account(self, vals, email):
        name = vals.get('name', '')
        cr = self.env['hr.department'].search([('id', '=', vals.get('department_id'))])
        department = '' if not cr else cr.complete_name
        gen = {"male": u"男", "female": u'女'}
        gender = gen.get(vals.get('gender', None), None)
        email_to = email
        subject = u"请开通新员工%s的微信(或钉钉/域账号/云学堂/BBS/OA/邮箱)账号！" % name
        content = u"%s的员工信息如下表。请您尽快开通相关账号!" % name
        self.env['mail.mail'].create({
                'body_html': u'''<p>{0}</p><table border="1px"><tbody>
                                <tr><td>账号:{1}</td><td>姓名:{2}</td><td>花名:{3}</td><td>部门:{4}</td></tr>
                                <tr><td>性别:{5}</td><td>工号:{6}</td><td>手机:{7}</td><td>邮箱:{8}</td></tr>
                                </tbody></table>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p><p>{9}</p>'''.format(content, vals.get('account', ''), vals.get('full_name', ''),
                                                            name, department, gender, vals.get('job_number', ''),
                                                            vals.get('mobile_phone', ''), vals.get('work_email', ''), self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    @api.model
    def create(self, vals):
        result = super(dtdream_hr_employee, self).create(vals)
        cr = self.env['hr.resume.approve'].search([])
        if cr.account:
            self.send_mail_remind_open_account(vals, cr.account.work_email)
        if cr.email:
            self.send_mail_remind_open_account(vals, cr.email.work_email)
        if cr.weixin:
            self.send_mail_remind_open_account(vals, cr.weixin.work_email)
        if cr.dingding:
            self.send_mail_remind_open_account(vals, cr.dingding.work_email)
        if cr.cloud:
            self.send_mail_remind_open_account(vals, cr.cloud.work_email)
        if cr.bbs:
            self.send_mail_remind_open_account(vals, cr.bbs.work_email)
        if cr.oa:
            self.send_mail_remind_open_account(vals, cr.oa.work_email)
        if cr.dodo:
            self.send_mail_remind_open_account(vals, cr.dodo.work_email)
        return result

    resume_log_nums = fields.Integer(compute='_compute_resume_log', string="履历记录")
    contract_log_nums = fields.Integer(compute='_compute_contract_log', string="合同记录")
    resume_view = fields.Boolean(string="履历是否可见", compute=_compute_resume_view)
    contract_view = fields.Boolean(string="合同是否可见", compute=_compute_contract_view)


class dtdream_resume_modify(models.Model):
    _name = 'dtdream.hr.resume.modify'
    _description = u"履历修改"
    _inherit = ['mail.thread']

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

    def _compute_name_equal_login(self):
        if self.env.user == self.name.user_id:
            self.is_login = True
        else:
            self.is_login = False

    def _compute_total_work(self):
        total = 0
        for rec in self.experince:
            total += rec.age_work
            self.total_work = total

    @api.constrains("experince")
    def check_start_end_time(self):
        for index, experince in enumerate(self.experince):
            start = experince.start_time
            end = experince.end_time
            for j in range(index):
                if not(self.experince[j].start_time > end or self.experince[j].end_time < start):
                    raise ValidationError("工作经历时间填写不合理,时间段之间存在重合!")

    @api.constrains('title')
    def constrains_title_record(self):
        if self.has_title and not len(self.title):
            raise ValidationError("请至少填写一条职称信息!")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        user_id = self._context.get('active_id', None)
        res = super(dtdream_resume_modify, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        if res['type'] == "form":
            doc = etree.XML(res['arch'])
            doc.xpath("//form")[0].set("create", "false")
            if not user_id:
                doc.xpath("//form")[0].set("edit", "false")
            res['arch'] = etree.tostring(doc)
        if res['type'] == "tree":
            if not user_id:
                doc = etree.XML(res['arch'])
                doc.xpath("//tree")[0].set("create", "false")
                doc.xpath("//tree")[0].set("edit", "false")
                res['arch'] = etree.tostring(doc)
        return res

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_mail_attend_mobile(self, email):
        email_to = email.work_email
        appellation = u'{0},您好：'.format(email.full_name)
        subject = u"手机号码变更通知"
        content = u"%s,员工手机号更改为%s,请您知悉!" % (self.name.full_name, self.mobile)
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    def send_mail_attend_resume(self, name, subject, content):
        email_to = name.work_email
        appellation = u'{0},您好：'.format(name.full_name)
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    def update_mobile_number(self):
        self.env['hr.employee'].search([('id', '=', self.name.id)]).write({"mobile_phone": self.mobile})
        cr = self.env["hr.resume.approve"].search([])
        if cr.email:
            self.send_mail_attend_mobile(cr.email)
        if cr.weixin:
            self.send_mail_attend_mobile(cr.weixin)
        if cr.dingding:
            self.send_mail_attend_mobile(cr.dingding)
        if cr.cloud:
            self.send_mail_attend_mobile(cr.cloud)
        if cr.oa:
            self.send_mail_attend_mobile(cr.cloud)

    def track_experience_change(self, resume):
        experince = [ex.id for ex in resume.experince]
        related = [ex.related for ex in self.experince]
        exper = u'''<li>工作经历:<table border='1px'><thead><tr>
                    <th style='width: 40px;'>动作</th><th style='width: 100px'>开始日期</th> <th style='width: 100px'> 结束日期</th>
                    <th style='width: 200px'>工作单位</th><th style='width: 150px;'>职位</th><th style='width: 200px'>备注</th>
                    </tr></thead><tbody>'''
        tracked = False
        for ex in self.experince:
            if ex.related in experince:
                cr = self.env['hr.employee.experience'].search([('id', '=', ex.related)])
                if ex.start_time != cr.start_time or ex.end_time != cr.end_time or ex.company != cr.company or ex.post != cr.post or ex.remark != cr.remark:
                    tracked = True
                    if ex.start_time != cr.start_time:
                        exper += u"<tr><td>修改</td><td style='color: red;'>%s</td>" % ex.start_time.replace("-", "/")
                    else:
                        exper += u"<tr><td>修改</td><td>{0}</td>".format(cr.start_time.replace("-", "/"))
                    if ex.end_time != cr.end_time:
                        exper += u"<td style='color: red;'>%s</td>" % ex.end_time.replace("-", "/")
                    else:
                        exper += u"<td>{0}</td>".format(cr.end_time.replace("-", "/"))
                    if ex.company != cr.company:
                        exper += u"<td style='color: red;'>{0}</td>".format(ex.company)
                    else:
                        exper += u"<td>{0}</td>".format(cr.company)
                    if ex.post != cr.post:
                        exper += u"<td style='color: red;'>{0}</td>".format(ex.post)
                    else:
                        exper += u"<td>{0}</td>".format(cr.post)
                    if ex.remark != cr.remark:
                        exper += u"<td style='color: red;'>{0}</td></tr>".format(ex.remark)
                    else:
                        exper += u"<td>{0}</td></tr>".format(cr.remark)
            else:
                tracked = True
                exper += u'''<tr style='color: red;'><td>新增</td><td>{0}</td><td>{1}</td><td>{2}</td>
                         <td>{3}</td><td>{4}</td></tr>'''.format(
                    ex.start_time.replace("-", "/"), ex.end_time.replace("-", "/"), ex.company, ex.post, ex.remark)
        for ex in resume.experince:
            if ex.id not in related:
                tracked = True
                exper += u'''<tr style='color: red;'><td>删除</td><td>{0}</td><td>{1}</td><td>{2}</td>
                         <td>{3}</td><td>{4}</td></tr>'''.format(
                    ex.start_time.replace("-", "/"), ex.end_time.replace("-", "/"), ex.company, ex.post, ex.remark)
        if not tracked:
            return ""
        exper += u"</tbody></table></li>"
        return exper.replace("False", "")

    def track_title_change(self, resume):
        title = [ex.id for ex in resume.title]
        related = [ex.related for ex in self.title]
        exper = u'''<li>职称信息:<table border='1px'><thead><tr>
                    <th style='width: 40px'>动作</th><th style='width: 200px'>职称名称</th> <th style='width: 200px'> 授予部门</th>
                    <th style='width: 100px'>授予年月</th><th style='width: 250px;'>备注</th></tr></thead><tbody>'''
        tracked = False
        for ex in self.title:
            if ex.related in title:
                cr = self.env['hr.employee.title'].search([('id', '=', ex.related)])
                if ex.name != cr.name or ex.depertment != cr.depertment or ex.date != cr.date or ex.remark != cr.remark:
                    tracked = True
                    if ex.name != cr.name:
                        exper += u"<tr><td>修改</td><td style='color: red;'>{0}</td>".format(ex.name)
                    else:
                        exper += u"<tr><td>修改</td><td>{0}</td>".format(cr.name)
                    if ex.depertment != cr.depertment:
                        exper += u"<td style='color: red;'>{0}</td>".format(ex.depertment)
                    else:
                        exper += u"<td>{0}</td>".format(cr.depertment)
                    if ex.date != cr.date:
                        exper += u"<td style='color: red;'>{0}</td>".format(ex.date.replace("-", "/"))
                    else:
                        exper += u"<td>{0}</td>".format(cr.date.replace("-", "/"))
                    if ex.remark != cr.remark:
                        exper += u"<td style='color: red;'>{0}</td></tr>".format(ex.remark)
                    else:
                        exper += u"<td>{0}</td></tr>".format(cr.remark)
            else:
                tracked = True
                exper += u'''<tr style='color: red;'><td>新增</td><td>{0}</td><td>{1}</td>
                <td>{2}</td><td>{3}</td></tr>'''.format(
                    ex.name, ex.depertment, ex.date.replace("-", "/"), ex.remark)
        for ex in resume.title:
            if ex.id not in related:
                tracked = True
                exper += u'''<tr style='color: red;'><td>删除</td><td>{0}</td><td>{1}</td>
                <td>{2}</td><td>{3}</td></tr>'''.format(
                    ex.name, ex.depertment, ex.date.replace("-", "/"), ex.remark)
        if not tracked:
            return ""
        exper += u"</tbody></table></li>"
        return exper.replace("False", "")

    def track_degree_change(self, resume):
        has_degree = {"0": u'是', "1": u'否'}
        degree = [ex.id for ex in resume.degree]
        related = [ex.related for ex in self.degree]
        exper = u'''<li>学历信息:<table border="1px"><thead><tr>
                    <th style='width: 40px'>动作</th><th style='width: 55px'>专科及以上学历</th> <th style='width: 50px'>是否获得学位</th>
                    <th style='width: 100px'>在校时间(始)</th><th style='width: 100px;'>在校时间(止)</th>
                    <th style='width: 245px'>学校</th><th style='width: 200px'>专业</th></tr></thead><tbody>'''
        tracked = False
        for ex in self.degree:
            if ex.related in degree:
                cr = self.env['hr.employee.degree'].search([('id', '=', ex.related)])
                if ex.degree != cr.degree or ex.has_degree != cr.has_degree or ex.entry_time != cr.entry_time or \
                                ex.leave_time != cr.leave_time or ex.school != cr.school or ex.major != cr.major:
                    tracked = True
                    if ex.degree != cr.degree:
                        exper += u"<tr><td>修改</td><td style='color: red;'>{0}</td>".format(ex.degree)
                    else:
                        exper += u"<tr><td>修改</td><td>{0}</td>".format(cr.degree)
                    if ex.has_degree != cr.has_degree:
                        exper += u"<td style='color: red;'>{0}</td>".format(has_degree.get(ex.has_degree))
                    else:
                        exper += u"<td>{0}</td>".format(has_degree.get(cr.has_degree))
                    if ex.entry_time != cr.entry_time:
                        exper += u"<td style='color: red;'>{0}</td>".format(ex.entry_time.replace("-", "/"))
                    else:
                        exper += u"<td>{0}</td>".format(cr.entry_time.replace("-", "/"))
                    if ex.leave_time != cr.leave_time:
                        exper += u"<td style='color: red;'>{0}</td>".format(ex.leave_time.replace("-", "/"))
                    else:
                        exper += u"<td>{0}</td>".format(cr.leave_time.replace("-", "/"))
                    if ex.school != cr.school:
                        exper += u"<td style='color: red;'>{0}</td>".format(ex.school)
                    else:
                        exper += u"<td>{0}</td>".format(cr.school)
                    if ex.major != cr.major:
                        exper += u"<td style='color: red;'>{0}</td></tr>".format(ex.major)
                    else:
                        exper += u"<td>{0}</td></tr>".format(cr.major)
            else:
                tracked = True
                exper += u'''<tr style='color: red;'><td>新增</td><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td>
                <td>{4}</td><td>{5}</td></tr>'''.format(
                    ex.degree, has_degree.get(ex.has_degree), ex.entry_time.replace("-", "/"), ex.leave_time.replace("-", "/"), ex.school, ex.major)
        for ex in resume.degree:
            if ex.id not in related:
                tracked = True
                exper += u'''<tr style='color: red;'><td>删除</td><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td>
                <td>{4}</td><td>{5}</td></tr>'''.format(
                    ex.degree, has_degree.get(ex.has_degree), ex.entry_time.replace("-", "/"), ex.leave_time.replace("-", "/"), ex.school, ex.major)
        if not tracked:
            return ""
        exper += u"</tbody></table></li>"
        return exper.replace("False", "")

    def track_language_change(self, resume):
        language = [ex.id for ex in resume.language]
        related = [ex.related for ex in self.language]
        exper = u'''<li>外语信息:<table border="1px"><thead><tr>
                    <th style='width: 40px'>动作</th><th style='width: 100px'>外语语种</th> <th style='width: 250px'> 证书名称</th>
                    <th style='width: 150px;white-space:nowrap'>考试结果或分数</th><th style='width: 250px'>备注</th>
                    </tr></thead><tbody>'''
        tracked = False
        for ex in self.language:
            if ex.related in language:
                cr = self.env['hr.employee.language'].search([('id', '=', ex.related)])
                if ex.langange != cr.langange or ex.cerdit != cr.cerdit or ex.result != cr.result or ex.remark != cr.remark:
                    tracked = True
                    if ex.langange != cr.langange:
                        exper += u"<tr><td>修改</td><td style='color: red;'>{0}</td>".format(ex.langange)
                    else:
                        exper += u"<tr><td>修改</td><td>{0}</td>".format(cr.langange)
                    if ex.cerdit != cr.cerdit:
                        exper += u"<td style='color: red;'>{0}</td>".format(ex.cerdit)
                    else:
                        exper += u"<td>{0}</td>".format(cr.cerdit)
                    if ex.result != cr.result:
                        exper += u"<td style='color: red;'>{0}</td>".format(ex.result)
                    else:
                        exper += u"<td>{0}</td>".format(cr.result)
                    if ex.remark != cr.remark:
                        exper += u"<td style='color: red;'>{0}</td></tr>".format(ex.remark)
                    else:
                        exper += u"<td>{0}</td></tr>".format(cr.remark)
            else:
                tracked = True
                exper += u'''<tr style='color: red;'><td>新增</td><td>{0}</td><td>{1}</td><td>{2}</td><td>
                {3}</td></tr>'''.format(ex.langange, ex.cerdit, ex.result, ex.remark)
        for ex in resume.language:
            if ex.id not in related:
                tracked = True
                exper += u'''<tr style='color: red;'><td>删除</td><td>{0}</td><td>{1}</td><td>{2}</td><td>
                {3}</td></tr>'''.format(ex.langange, ex.cerdit, ex.result, ex.remark)
        if not tracked:
            return ""
        exper += u"</tbody></table></li>"
        return exper.replace("False", "")

    @api.multi
    def track_fields_change(self):
        self.signal_workflow('btn_submit')
        resume = self.env['dtdream.hr.resume'].search([('name.id', '=', self.name.id)])
        body = ""
        tab = u"<ul class='o_mail_thread_message_tracking'>"
        if resume.mobile != self.mobile:
            body += tab + u"<li>手机号:<span>{0}</span>--><span>{1}</span></li>".format(resume.mobile, self.mobile)
        if resume.icard != self.icard:
            body += u"<li>身份证:<span>{0}</span>--><span>{1}</span></li>".format(resume.icard, self.icard)
        if resume.home_address != self.home_address:
            body += u"<li>居住地址:<span>{0}</span>--><span>{1}</span></li>".format(resume.home_address, self.home_address)
        if resume.marry != self.marry:
            marry = {"0": u"未婚", "1": u"已婚", "2": u"离异"}
            body += u"<li>婚姻:<span>{0}</span>--><span>{1}</span></li>".format(marry.get(resume.marry), marry.get(self.marry))
        if resume.child != self.child:
            body += u"<li>子女数:<span>{0}</span>--><span>{1}</span></li>".format(resume.child, self.child)
        if resume.has_title != self.has_title:
            body += u"<li>是否有职称信息:<span>{0}</span>--><span>{1}</span></li>".format(resume.has_title, self.has_title)
        exper = self.track_experience_change(resume)
        title = self.track_title_change(resume)
        degree = self.track_degree_change(resume)
        langange = self.track_language_change(resume)
        body += exper + title + degree + langange
        if not body:
            return
        body += u"</ul>"
        self.message_post(body=body)

    def update_resume_record(self):
        resume = self.env['dtdream.hr.resume'].search([('name.id', '=', self.name.id)])
        if self.marry != resume.marry:
            resume.write({'marry': self.marry})
        if self.child != resume.child:
            resume.write({'child': self.child})
        if self.icard != resume.icard:
            resume.write({'icard': self.icard})
        if self.mobile != resume.mobile:
            resume.write({'mobile': self.mobile})
            self.update_mobile_number()
        if self.home_address != resume.home_address:
            resume.write({'home_address': self.home_address})
        if self.has_title != resume.has_title:
            resume.write({'has_title': self.has_title})

        resume.experince.unlink()
        for experince in self.experince:
            self.env['hr.employee.experience'].create({'resume': resume.id, 'start_time': experince.start_time,
                                                       'end_time': experince.end_time, 'age_work': experince.age_work,
                                                       'company': experince.company, 'post': experince.post,
                                                       'remark': experince.remark})

        resume.title.unlink()
        for title in self.title:
            self.env['hr.employee.title'].create({'resume': resume.id, 'name': title.name,
                                                 'depertment': title.depertment, 'date': title.date,
                                                  'remark': title.remark})

        resume.degree.unlink()
        if self.has_title:
            for degree in self.degree:
                self.env['hr.employee.degree'].create({'resume': resume.id, 'degree': degree.degree,
                                                      'has_degree': degree.has_degree, 'entry_time': degree.entry_time,
                                                       'leave_time': degree.leave_time, 'school': degree.school,
                                                       'major': degree.major})

        resume.language.unlink()
        for lan in self.language:
            self.env['hr.employee.language'].create({'resume': resume.id, 'langange': lan.langange,
                                                     'cerdit': lan.cerdit, 'result': lan.result,
                                                     'remark': lan.remark})

    name = fields.Many2one("hr.employee", string="花名", readonly="True")
    is_graduate = fields.Boolean(string="是应届毕业生")
    workid = fields.Char(string="工号", readonly="True")
    department = fields.Char(string="部门", readonly="True")
    has_title = fields.Boolean(string="是否有职称信息")
    marry = fields.Selection([("0", "未婚"), ("1", "已婚"), ("2", "离异")], string="婚姻", required=True)
    child = fields.Integer(string="子女数")
    icard = fields.Char(string="身份证", required=True)
    mobile = fields.Char(string="手机号", required=True)
    home_address = fields.Char(string="居住地址", required=True)
    experince = fields.One2many("hr.employee.experience", "resume_modify", "工作经历")
    total_work = fields.Float(string="合计工龄", compute=_compute_total_work)
    title = fields.One2many("hr.employee.title", "resume_modify", "职称信息")
    degree = fields.One2many("hr.employee.degree", "resume_modify", "学历信息")
    language = fields.One2many("hr.employee.language", "resume_modify", "外语信息")
    resume_approve = fields.Many2one('hr.employee', string="当前审批人")
    is_login = fields.Boolean(string="登入", compute=_compute_name_equal_login)
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
        self.send_mail_attend_resume(approve, subject=u'%s提交了员工履历信息修改,请您审批!' % self.name.name,
                                     content=u"%s提交了员工履历信息修改,等待您的审批!" % self.name.full_name)
        self.write({'state': '1', 'resume_approve': approve.id})

    @api.multi
    def wkf_done(self):
        self.update_resume_record()
        self.write({'state': '99', 'resume_approve': '', "approved": [(4, self.resume_approve.id)]})

    @api.multi
    def wkf_reject(self):
        self.write({'state': '-1', 'resume_approve': '', "approved": [(4, self.resume_approve.id)]})







