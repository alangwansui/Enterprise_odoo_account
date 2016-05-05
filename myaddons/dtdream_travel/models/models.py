# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
from openerp.exceptions import ValidationError
from datetime import datetime
import re


class dtdream_travel(models.Model):
    _name = 'dtdream.travel.chucha'
    _inherit = ['mail.thread']

    warning_digit = {
                    'title': u"提示",
                    'message': u"输入费用含非数字，或者输入的数字不合法!"
                }

    warning_order = {
                'title': u"提示",
                'message': u"审批人必须按顺序填写!"
            }

    @api.onchange('traveling_fee')
    @api.constrains('traveling_fee')
    def _check_traveling_fee(self):
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        if self.traveling_fee:
            if not p.search(str(self.traveling_fee)):
                self.traveling_fee = False
                return {"warning": self.warning_digit}
        self._compute_total_fee()

    @api.onchange('incity_fee')
    def _check_incity_fee(self):
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        if self.incity_fee:
            if not p.search(str(self.incity_fee)):
                self.incity_fee = False
                return {"warning": self.warning_digit}
        self._compute_total_fee()

    @api.onchange('hotel_expense')
    def _check_hotel_fee(self):
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        if self.hotel_expense:
            if not p.search(str(self.hotel_expense)):
                self.hotel_expense = False
                return {"warning": self.warning_digit}
        self._compute_total_fee()

    @api.onchange('other_expense')
    def _check_other_fee(self):
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        if self.other_expense:
            if not p.search(str(self.other_expense)):
                self.other_expense = False
                return {"warning": self.warning_digit}
        self._compute_total_fee()

    def _compute_total_fee(self):
        self.total = float(self.traveling_fee) + float(self.incity_fee) +\
                     float(self.hotel_expense) + float(self.other_expense)

    @api.one
    def has_edit_shenpiren(self):
        if self.state == "0":
            self.has_edit = True
        elif self.shenpi_first.user_id == self.env.user and self.state == "1":
            self.has_edit = True
        elif self.shenpi_second.user_id == self.env.user and self.state == "2":
            self.has_edit = True
        elif self.shenpi_third.user_id == self.env.user and self.state == "3":
            self.has_edit = True
        elif self.shenpi_fourth.user_id == self.env.user and self.state == "4":
            self.has_edit = True
        elif self.shenpi_fifth.user_id == self.env.user and self.state == "5":
            self.has_edit = True
        else:
            self.has_edit = False

    @api.depends("name")
    def _compute_shenpi_person(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id.complete_name
            cr = rec.env["dtdream.travel.chucha"].search([("name.id", "=", rec.name.id)], limit=1, order="id desc")
            if cr.shenpi_first:
                rec.shenpi_first = cr.shenpi_first
            rec.shenpi_second = cr.shenpi_second
            rec.shenpi_third = cr.shenpi_third
            rec.shenpi_fourth = cr.shenpi_fourth
            rec.shenpi_fifth = cr.shenpi_fifth

    @api.onchange("shenpi_second")
    @api.constrains("shenpi_second")
    def check_shenpi_first(self):
        if not self.shenpi_first.id and self.shenpi_second.id:
            self.shenpi_second = False
            return {"warning": self.warning_order}

    @api.onchange("shenpi_third")
    @api.constrains("shenpi_third")
    def check_shenpi_second(self):
        if not self.shenpi_second.id and self.shenpi_third.id:
            self.shenpi_third = False
            return {"warning": self.warning_order}

    @api.onchange("shenpi_fourth")
    @api.constrains("shenpi_fourth")
    def check_shenpi_third(self):
        if not self.shenpi_third.id and self.shenpi_fourth.id:
            self.shenpi_fourth = False
            return {"warning": self.warning_order}

    @api.onchange("shenpi_fifth")
    @api.constrains("shenpi_fifth")
    def check_shenpi_fourth(self):
        if not self.shenpi_fourth.id and self.shenpi_fifth.id:
            self.shenpi_fifth = False
            return {"warning": self.warning_order}

    @api.constrains("journey_id")
    def _check_journey_details(self):
        if len(self.journey_id) <= 0:
            raise ValidationError(u"请至少填写一条行程记录!")

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != '0'and rec.env.user.id != 1:
                raise osv.except_osv(u'审批流程中的出差申请单无法删除!')
            return super(dtdream_travel, self).unlink(cr, uid, ids, context)

    @api.one
    def _compute_is_current(self):
        if self.shenpiren.user_id == self.env.user:
            self.is_current = True
        else:
            self.is_current = False

    @api.one
    def _compute_can_restart(self):
        if self.env.user == self.name.user_id or self.env.user == self.create_uid:
            self.can_restart = True
        else:
            self.can_restart = False

    @staticmethod
    def _get_current_time(state=False):
        if state:
            return datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        return datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_mail(self, subject, content, email_to, email_cc="", wait=False):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.travel.chucha' % self.id
        url = base_url+link
        email_to = email_to
        email_cc = "" if email_cc == email_to else email_cc
        subject = subject
        if wait:
            appellation = u'{0},您好：'.format(self.name.user_id.name)
        else:
            appellation = u'{0},您好：'.format(self.shenpiren.user_id.name)
        content = content
        self.env['mail.mail'].create({
                'body_html': '''<p>%s</p>
                                <p>%s</p>
                                <p>点击链接进入查看:
                                <a href="%s">%s</a></p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, url, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'email_cc': '%s' % email_cc,
                'auto_delete': False,
            }).send()

    @api.onchange('name')
    def _shenpi_first_domain(self):
        assitand = self.name.department_id.assitant_id
        ancestors = []
        if assitand:
            self.shenpi_first = assitand[0]
            if len(assitand) > 1:
                for x in assitand:
                    ancestors.append(x.id)
                return {'domain': {'shenpi_first': [('id', 'in', ancestors)]}}
        else:
            self.shenpi_first = False
            return {'domain': {'shenpi_first': [('id', '=', False)]}}

    @api.constrains("journey_id")
    def _check_start_end_time(self):
        """检查各行程间时间是否冲突，或者与外出公干时间冲突"""
        min_start = ""
        cr = self.env["dtdream_hr_business.business_detail"].search([("business.name.id", "=", self.name.id),
                                                                     ("business.state", "!=", "-1")])
        for journey in self.journey_id:
            for detail in cr:
                if detail.startTime[:10] < journey.starttime < detail.endTime[:10] or \
                                        detail.startTime[:10] < journey.endtime < detail.endTime[:10]:
                    raise ValidationError("{0}到{1}时间与外出公干时间重合".format(journey.starttime, journey.endtime))
            if journey.starttime < min_start:
                raise ValidationError("出差时间与结束时间填写不合理,各行程间时间存在冲突!")
            min_start = journey.endtime

    name = fields.Many2one('hr.employee', string="申请人", required=True, default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]))
    shenpi_first = fields.Many2one('hr.employee', string="第一审批人", help="部门行政助理", required=True)
    shenpi_second = fields.Many2one('hr.employee', string="第二审批人", help="部门主管", default=_compute_shenpi_person)
    shenpi_third = fields.Many2one('hr.employee', string="第三审批人", help="受益部门权签人(当受益部门与权签部门不一致时)", default=_compute_shenpi_person)
    shenpi_fourth = fields.Many2one('hr.employee', string="第四审批人", default=_compute_shenpi_person)
    shenpi_fifth = fields.Many2one('hr.employee', string="第五审批人", default=_compute_shenpi_person)
    shenpiren = fields.Many2one('hr.employee', string="当前审批人")
    is_current = fields.Boolean(string="是否当前审批人", compute=_compute_is_current)
    can_restart = fields.Boolean(string="是否有权限重启", compute=_compute_can_restart)
    has_edit = fields.Boolean(compute=has_edit_shenpiren, string="是否有权限编辑审批人", default=True)
    workid = fields.Char(string="工号", compute=_compute_shenpi_person)
    department = fields.Char(string="部门", compute=_compute_shenpi_person)
    department_shouyi = fields.Many2one('hr.department', string="受益部门", required=True)
    create_time = fields.Datetime(string="申请时间", default=lambda self: datetime.now(), readonly=True)
    traveling_fee = fields.Char(string="在途交通费(元)", required=True)
    incity_fee = fields.Char(string="市内交通费(元)", required=True)
    hotel_expense = fields.Char(string="住宿费(元)", required=True)
    other_expense = fields.Char(string="其它费(元)", required=True)
    total = fields.Float(string="合计(元)", readonly=True)
    journey_id = fields.One2many("dtdream.travel.journey", "travel_id", string="行程")
    employ = fields.Many2one("hr.employee", string="员工")
    approve = fields.Many2many("hr.employee", string="已批准的审批人")
    state = fields.Selection(
        [('0', '草稿'),
         ('1', '一级审批'),
         ('2', '二级审批'),
         ('3', '三级审批'),
         ('4', '四级审批'),
         ('5', '五级审批'),
         ('-1', '驳回'),
         ('99', '完成')], string="状态", default="0")

    @api.multi
    def wkf_draft(self):
        if self.state == "-1":
            self.message_post(body=u'重启流程,驳回 --> 草稿 '+u'下一审批人:'+self.shenpi_first.name)
        self.write({'state': '0', "shenpiren": ''})

    @api.multi
    def wkf_approve1(self):
        self.write({'state': '1', "shenpiren": self.shenpi_first.id})
        self.message_post(body=u'提交,草稿 --> 一级审批 '+u'下一审批人:' + self.shenpi_first.name)
        self.send_mail(u"{0}于{1}提交了出差申请,请您审批!".format(self.name.name, self.create_time[:10]),
                       u"%s提交了出差申请,等待您的审批" % self.name.name, email_to=self.shenpi_first.work_email)

    @api.multi
    def wkf_approve2(self):
        if self.shenpi_second.id:
            if self.department_shouyi != self.name.department_id and not self.shenpi_third:
                raise osv.except_osv(u'申请人与受益部门不是同一部门，请填写第三审批人!')
            content = u'%s批准了您的出差申请！' % self.shenpi_first.name
            self.send_mail(subject=u"{0}您于{1}提交的出差申请已被{2}批准,请您查看!".format(
                self.name.name, self.create_time[:10], self.shenpi_first.name), content=content,
                email_to=self.name.work_email, email_cc=self.create_uid.email, wait=True)
            self.send_mail(u"{0}于{1}提交了出差申请,请您审批!".format(self.name.name, self.create_time[:10]),
                           u"%s提交了出差申请,等待您的审批" % self.name.name, email_to=self.shenpi_second.work_email)
            self.write({'state': '2', "shenpiren": self.shenpi_second.id, "approve": [(4, self.shenpi_first.id)]})
            self.message_post(body=u'批准,一级审批 --> 二级审批 '+u'下一审批人:' + self.shenpi_second.name)
        else:
            raise osv.except_osv(u'第二审批人为必填项!')

    @api.multi
    def wkf_approve3(self):
        if self.shenpi_third.id:
            self.write({'state': '3', "shenpiren": self.shenpi_third.id, "approve": [(4, self.shenpi_second.id)]})
            self.message_post(body=u' 批准,二级审批 --> 三级审批 '+u'下一审批人:' + self.shenpi_third.name)
            self.send_mail(u"{0}于{1}提交了出差申请,请您审批!".format(self.name.name, self.create_time[:10]),
                           u"%s提交了出差申请,等待您的审批" % self.name.name, email_to=self.shenpi_third.work_email)
        else:
            self.write({'state': '99', "shenpiren": '', "approve": [(4, self.shenpi_second.id)]})
            self.message_post(body=u' 批准,二级审批 --> 完成 ')
        content = u'%s批准了您的出差申请！' % self.shenpi_second.name
        self.send_mail(subject=u"{0}您于{1}提交的出差申请已被{2}批准,请您查看!".format(
            self.name.name, self.create_time[:10], self.shenpi_second.name), content=content,
            email_to=self.name.work_email, email_cc=self.create_uid.email, wait=True)

    @api.multi
    def wkf_approve4(self):
        if self.shenpi_fourth.id:
            self.write({'state': '4', "shenpiren": self.shenpi_fourth.id, "approve": [(4, self.shenpi_third.id)]})
            self.message_post(body=u' 批准,三级审批 --> 四级审批 '+u'下一审批人:' + self.shenpi_fourth.name)
            self.send_mail(u"{0}于{1}提交了出差申请,请您审批!".format(self.name.name, self.create_time[:10]),
                           u"%s提交了出差申请,等待您的审批" % self.name.name, email_to=self.shenpi_fourth.work_email)
        else:
            self.write({'state': '99', "shenpiren": '', "approve": [(4, self.shenpi_third.id)]})
            self.message_post(body=u' 批准,三级审批 --> 完成 ')
        content = u'%s批准了您的出差申请！' % self.shenpi_third.name
        self.send_mail(subject=u"{0}您于{1}提交的出差申请已被{2}批准,请您查看!".format(
            self.name.name, self.create_time[:10], self.shenpi_third.name), content=content,
            email_to=self.name.work_email, email_cc=self.create_uid.email, wait=True)

    @api.multi
    def wkf_approve5(self):
        if self.shenpi_fifth.id:
            self.write({'state': '5', "shenpiren": self.shenpi_fifth.id, "approve": [(4, self.shenpi_fourth.id)]})
            self.message_post(body=u' 批准,四级审批 --> 五级审批 '+u'下一审批人:' + self.shenpi_fifth.name)
            self.send_mail(u"{0}于{1}提交了出差申请,请您审批!".format(self.name.name, self.create_time[:10]),
                           u"%s提交了出差申请,等待您的审批" % self.name.name, email_to=self.shenpi_fifth.work_email)
        else:
            self.write({'state': '99', "shenpiren": '', "approve": [(4, self.shenpi_fourth.id)]})
            self.message_post(body=u' 批准,四级审批 --> 完成 ')
        content = u'%s批准了您的出差申请！' % self.shenpi_fourth.name
        self.send_mail(subject=u"{0}您于{1}提交的出差申请已被{2}批准,请您查看!".format(
            self.name.name, self.create_time[:10], self.shenpi_fourth.name), content=content,
            email_to=self.name.work_email, email_cc=self.create_uid.email, wait=True)

    @api.multi
    def wkf_done(self):
        content = u'%s批准了您的出差申请,审批已完成！' % self.shenpi_fifth.name
        self.send_mail(subject=u"{0}您于{1}提交的出差申请已被{2}批准,请您查看!".format(
            self.name.name, self.create_time[:10], self.shenpi_fifth.name), content=content,
            email_to=self.name.work_email, email_cc=self.create_uid.email, wait=True)
        self.write({'state': '99', "shenpiren": '', "approve": [(4, self.shenpi_fifth.id)]})
        self.message_post(body=u' 批准,五级审批 --> 完成 ')

    @api.multi
    def wkf_reject(self):
        content = u'%s驳回了您的出差申请！' % self.shenpiren.name
        self.send_mail(subject=u"{0}您于{1}提交的出差申请已被{2}驳回,请您查看!".format(
            self.name.name, self.create_time[:10], self.shenpiren.name), content=content,
            email_to=self.name.work_email, email_cc=self.create_uid.email, wait=True)
        self.write({'state': '-1', "shenpiren": ''})


class dtdream_travel_journey(models.Model):
    _name = "dtdream.travel.journey"

    @api.constrains("startaddress", "endaddress", "starttime", "endtime")
    def _check_start_end_address(self):
        if not self.startaddress or not self.endaddress or not self.starttime or not self.endtime:
            raise ValidationError(u"出发地,目的地,出差时间,结束时间为必填项!")

    travel_id = fields.Many2one("dtdream.travel.chucha", string="申请人")
    name = fields.Char(related="travel_id.name.full_name", string="姓名")
    starttime = fields.Date(default=fields.Date.today, string="出差时间")
    endtime = fields.Date(string="结束时间")
    startaddress = fields.Char(string="出发地")
    endaddress = fields.Char(string="目的地")
    reason = fields.Text(string="出差原因")

    _sql_constraints = [
        ("date_check", "CHECK(starttime < endtime)", u'结束时间必须大于出差时间')
    ]


class dtdream_hr(models.Model):
    _inherit = 'hr.employee'

    @api.depends("travel_ids")
    def _compute_chucha_log(self):
        cr = self.env["dtdream.travel.chucha"].search([("name.id", "=", self.id)])
        self.chucha_log_nums = len(cr)

    @api.one
    def _compute_has_view(self):
        if self.user_id == self.env.user:
            self.can_view = True
        else:
            self.can_view = False

    can_view = fields.Boolean(compute="_compute_has_view")
    travel_ids = fields.One2many("dtdream.travel.chucha", "employ", string="出差")
    chucha_log_nums = fields.Integer(compute='_compute_chucha_log', string="出差记录")
