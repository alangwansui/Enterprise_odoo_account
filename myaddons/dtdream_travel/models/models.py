# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
from datetime import datetime, timedelta
import re


class dtdream_travel(models.Model):
    _name = 'dtdream.travel.chucha'
    _inherit = ['mail.thread']

    warning_digit = {
                    'title': u"提示",
                    'message': u"费用必须输入数字!"
                }

    warning_order = {
                'title': u"提示",
                'message': u"审批人必须按顺序填写!"
            }

    @api.onchange('traveling_fee')
    @api.constrains('traveling_fee')
    def _check_traveling_fee(self):
        p = re.compile(r'(\d+)|(\d+\.\d+)')
        if self.traveling_fee:
            if not p.search(str(self.traveling_fee)):
                self.traveling_fee = False
                return {"warning": self.warning_digit}
        self._compute_total_fee()

    @api.onchange('incity_fee')
    def _check_incity_fee(self):
        p = re.compile(r'(\d+)|(\d+\.\d+)')
        if self.incity_fee:
            if not p.search(str(self.incity_fee)):
                self.incity_fee = False
                return {"warning": self.warning_digit}
        self._compute_total_fee()

    @api.onchange('hotel_expense')
    def _check_hotel_fee(self):
        p = re.compile(r'(\d+)|(\d+\.\d+)')
        if self.hotel_expense:
            if not p.search(str(self.hotel_expense)):
                self.hotel_expense = False
                return {"warning": self.warning_digit}
        self._compute_total_fee()

    @api.onchange('other_expense')
    def _check_other_fee(self):
        p = re.compile(r'(\d+)|(\d+\.\d+)')
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
            rec.shenpi_first = rec.name.department_id.assitant_id
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

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if (rec.state != '0' and uid != 1) or (rec.state != '99' and uid == 1):
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
            return (datetime.now() + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
        return (datetime.now() + timedelta(hours=8)).strftime("%m/%d/%Y %H:%M:%S")

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def send_mail(self, subject, content):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.travel.chucha' % self.id
        url = base_url+link
        email_to = self.name.user_id.email
        if self.name.user_id != self.create_uid:
            email_cc = self.create_uid.email
        else:
            email_cc = ""
        subject = subject
        appellation = u'您好：'
        content = content
        self.env['mail.mail'].create({
                'body_html': '''<p>%s</p>
                                <p>%s</p>
                                <p>点击链接进入查看:</p>
                                <ul><li><a href="%s">%s</a></li></ul>
                                <pre>
                                <p>数梦企业应用平台<p>
                                <p>%s<p></pre>''' % (appellation, content, url, url, self._get_current_time(state=True)),
                'subject': '%s' % subject,
                'email_to': '%s' % email_to,
                'email_cc': '%s' % email_cc,
                'auto_delete': False,
            }).send()

    name = fields.Many2one('hr.employee', string="申请人", required=True)
    shenpi_first = fields.Many2one('hr.employee', string="第一审批人", help="部门行政助理", required=True, default=_compute_shenpi_person)
    shenpi_second = fields.Many2one('hr.employee', string="第二审批人", help="部门主管", default=_compute_shenpi_person)
    shenpi_third = fields.Many2one('hr.employee', string="第三审批人", help="受益部门权签人(当受益部门与权签部门不一致时)", default=_compute_shenpi_person)
    shenpi_fourth = fields.Many2one('hr.employee', string="第四审批人", default=_compute_shenpi_person)
    shenpi_fifth = fields.Many2one('hr.employee', string="第五审批人", default=_compute_shenpi_person)
    shenpiren = fields.Many2one('hr.employee', string="当前审批人")
    can_restart = fields.Boolean(string="是否有权限重启", compute=_compute_can_restart)
    is_current = fields.Boolean(string="是否当前审批人", compute=_compute_is_current)
    has_edit = fields.Boolean(compute=has_edit_shenpiren, string="是否有权限编辑审批人", default=True)
    workid = fields.Char(string="工号", compute=_compute_shenpi_person)
    department = fields.Char(string="部门", compute=_compute_shenpi_person)
    department_shouyi = fields.Many2one('hr.department', string="受益部门")
    create_time = fields.Char(string="申请时间", default=lambda self: self._get_current_time(), readonly=True)
    traveling_fee = fields.Char(string="在途交通费", required=True)
    incity_fee = fields.Char(string="市内交通费", required=True)
    hotel_expense = fields.Char(string="住宿费", required=True)
    other_expense = fields.Char(string="其它费", required=True)
    total = fields.Float(string="合计", readonly=True)
    journey_id = fields.One2many("dtdream.travel.journey", "travel_id", string="行程")
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
            self.message_post(body=u'重启流程,驳回 --> 草稿 '+u'下一审批人:'+self.shenpi_first.name + u" 操作时间:" +
                                   self._get_current_time())
        self.write({'state': '0', "shenpiren": ''})

    @api.multi
    def wkf_approve1(self):
        content = u'您于%s提交了出差申请！<p>申请单创建人:%s</p>' % (self._get_current_time(state=True), self.create_uid.name)
        self.send_mail(subject=u'出差申请提交', content=content, draft=True)
        self.write({'state': '1', "shenpiren": self.shenpi_first.id})
        self.message_post(body=u'提交,草稿 --> 一级审批 '+u'下一审批人:' + self.shenpi_first.name + u" 操作时间:" +
                               self._get_current_time())

    @api.multi
    def wkf_approve2(self):
        if self.shenpi_second.id:
            content = u'%s于%s批准了您的出差申请！<p>下一审批人:%s</p>' % (self.shenpi_first.name, self._get_current_time(state=True), self.shenpi_second.name)
            self.send_mail(subject=u'出差申请审批通过', content=content)
            self.write({'state': '2', "shenpiren": self.shenpi_second.id, "approve": [(4, self.shenpi_first.id)]})
            self.message_post(body=u'批准,一级审批 --> 二级审批 '+u'下一审批人:' + self.shenpi_second.name +
                                   u" 操作时间:" + self._get_current_time())
        else:
            raise osv.except_osv(u'第二审批人不能为空!')

    @api.multi
    def wkf_approve3(self):
        if self.shenpi_third.id:
            self.write({'state': '3', "shenpiren": self.shenpi_third.id, "approve": [(4, self.shenpi_second.id)]})
            self.message_post(body=u' 批准,二级审批 --> 三级审批 '+u'下一审批人:' + self.shenpi_third.name +
                                   u" 操作时间:" + self._get_current_time())
        elif self.department_shouyi:
            raise osv.except_osv(u'第三审批人不能为空!')
        else:
            self.write({'state': '99', "shenpiren": '', "approve": [(4, self.shenpi_second.id)]})
            self.message_post(body=u' 批准,二级审批 --> 完成 '+u" 操作时间:" + self._get_current_time())
        content = u'%s于%s批准了您的出差申请！<p>下一审批人:%s</p>' % (self.shenpi_second.name, self._get_current_time(state=True), self.shenpi_third.name)
        self.send_mail(subject=u'出差申请审批通过', content=content)

    @api.multi
    def wkf_approve4(self):
        if self.shenpi_fourth.id:
            self.write({'state': '4', "shenpiren": self.shenpi_fourth.id, "approve": [(4, self.shenpi_third.id)]})
            self.message_post(body=u' 批准,三级审批 --> 四级审批 '+u'下一审批人:' + self.shenpi_fourth.name +
                                   u" 操作时间:" + self._get_current_time())
        else:
            self.write({'state': '99', "shenpiren": '', "approve": [(4, self.shenpi_third.id)]})
            self.message_post(body=u' 批准,三级审批 --> 完成 '+u" 操作时间:" + self._get_current_time())
        content = u'%s于%s批准了您的出差申请！<p>下一审批人:%s</p>' % (self.shenpi_third.name, self._get_current_time(state=True), self.shenpi_fourth.name)
        self.send_mail(subject=u'出差申请审批通过', content=content)

    @api.multi
    def wkf_approve5(self):
        if self.shenpi_fifth.id:
            self.write({'state': '5', "shenpiren": self.shenpi_fifth.id, "approve": [(4, self.shenpi_fourth.id)]})
            self.message_post(body=u' 批准,四级审批 --> 五级审批 '+u'下一审批人:' + self.shenpi_fifth.name +
                                   u" 操作时间:" + self._get_current_time())
        else:
            self.write({'state': '99', "shenpiren": '', "approve": [(4, self.shenpi_fourth.id)]})
            self.message_post(body=u' 批准,四级审批 --> 完成 '+u" 操作时间:" + self._get_current_time())
        content = u'%s于%s批准了您的出差申请！<p>下一审批人:%s</p>' % (self.shenpi_fourth.name, self._get_current_time(state=True), self.shenpi_fifth.name)
        self.send_mail(subject=u'出差申请审批通过', content=content)

    @api.multi
    def wkf_done(self):
        content = u'%s于%s批准了您的出差申请,审批已完成！' % (self.shenpi_fifth.name, self._get_current_time(state=True))
        self.send_mail(subject=u'出差申请审批通过', content=content)
        self.write({'state': '99', "shenpiren": '', "approve": [(4, self.shenpi_fifth.id)]})
        self.message_post(body=u' 批准,五级审批 --> 完成 '+u" 操作时间:" + self._get_current_time())

    @api.multi
    def wkf_reject(self):
        content = u'%s于%s驳回了您的出差申请！' % (self.shenpiren.name, self._get_current_time(state=True))
        self.send_mail(subject=u'出差申请审批驳回', content=content)
        self.write({'state': '-1', "shenpiren": ''})


class dtdream_travel_journey(models.Model):
    _name = "dtdream.travel.journey"

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

