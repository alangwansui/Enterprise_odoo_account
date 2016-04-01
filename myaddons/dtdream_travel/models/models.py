# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_travel(models.Model):
    _name = 'dtdream.travel.chucha'

    @api.depends('traveling_fee', 'incity_fee', 'hotel_expense', 'other_expense')
    def _compute_expense_total(self):
        for rec in self:
            rec.total = rec.traveling_fee + rec.incity_fee + rec.hotel_expense + rec.other_expense

    @api.one
    def _compute_has_next(self):
        if self.state == "1":
            self.has_next = True
        elif self.state == "2" and self.shenpi_third.id:
            self.has_next = True
        elif self.state == "3" and self.shenpi_fourth.id:
            self.has_next = True
        elif self.state == "4" and self.shenpi_fifth.id:
            self.has_next = True
        else:
            self.has_next = False

    @api.one
    def _compute_has_next(self):
        if self.state == "1" and self.shenpiren_second.id:
            self.has_next = True
        elif self.state == "2" and self.shenpi_third.id:
            self.has_next = True
        elif self.state == "3" and self.shenpi_fourth.id:
            self.has_next = True
        elif self.state == "4" and self.shenpi_fifth.id:
            self.has_next = True
        else:
            self.has_next = False
            self.write({'state': '99', "shenpiren": ''})

    name = fields.Char(string="申请人", default=lambda self: self.env["hr.employee"].search(
        [("login", "=", self.env.user.login)]).name, readonly=True)
    shenpi_first = fields.Many2one('res.users', string="第一审批人")
    shenpi_second = fields.Many2one('res.users', string="第二审批人")
    shenpi_third = fields.Many2one('res.users', string="第三审批人")
    shenpi_fourth = fields.Many2one('res.users', string="第四审批人")
    shenpi_fifth = fields.Many2one('res.users', string="第五审批人")
    is_shenpiren = fields.Boolean(compute="_compute_is_shenpiren", string="是否当前审批人")
    has_next = fields.Boolean(compute="_compute_has_next", string="是否存在下一审批人")
    workid = fields.Char(string="工号", readonly=True, default=lambda self: self.env["hr.employee"].search(
        [("login", "=", self.env.user.login)]).job_number)
    deperment = fields.Char(string="部门", readonly=True, default=lambda self: self.env["hr.employee"].search(
        [("login", "=", self.env.user.login)]).department_id.name)
    reason = fields.Html(string="出差原因")
    traveling_fee = fields.Float(string="在途交通费")
    incity_fee = fields.Float(string="市内交通费")
    hotel_expense = fields.Float(string="住宿费")
    other_expense = fields.Float(string="其它费")
    total = fields.Float(compute=_compute_expense_total, string="合计")
    journey_id = fields.One2many("dtdream.travel.journey", "travel_id", string="行程")
    state = fields.Selection(
        [('0', '提交申请'),
         ('1', '第一审批人'),
         ('2', '第二审批人'),
         ('3', '第三审批人'),
         ('4', '第四审批人'),
         ('5', '第五审批人'),
         ('99', '结束'),
         ("-1", "reject")], string="状态", default="0")

    @api.multi
    def wkf_draft(self):
        self.write({'state': '0'})

    @api.multi
    def wkf_approve1(self):
        #self.shenpiren = self.shenpi_first
        self.write({'state': '1'})

    @api.multi
    def wkf_approve2(self):
        #if self.shenpi_second.id:
        #    self.shenpiren = self.shenpi_second
        self.write({'state': '2'})
        #else:
        #    self.write({'state': '99', "shenpiren": ''})

    @api.multi
    def wkf_approve3(self):
        # if self.shenpi_third.id:
        #     self.shenpiren = self.shenpi_third
        self.write({'state': '3'})
        # else:
        #     self.write({'state': '99', "shenpiren": ''})

    @api.multi
    def wkf_approve4(self):
        # if self.shenpi_fourth.id:
        #     self.shenpiren = self.shenpi_fourth
        self.write({'state': '4'})
        # else:
        #     self.write({'state': '99', "shenpiren": ''})

    @api.multi
    def wkf_approve5(self):
        # if self.shenpi_fifth.id:
        #     self.shenpiren = self.shenpi_fifth
        self.write({'state': '5'})
        # else:
        #     self.write({'state': '99', "shenpiren": ''})

    @api.multi
    def wkf_done(self):
        self.write({'state': '99'})


class dtdream_travel_journey(models.Model):
    _name = "dtdream.travel.journey"

    travel_id = fields.Many2one("dtdream.travel.chucha", string="申请人")
    name = fields.Char(related="travel_id.name", string="姓名")
    starttime = fields.Date(default=fields.Date.today, string="出差时间")
    endtime = fields.Date(string="结束时间")
    startaddress = fields.Char(string="出发地")
    endaddress = fields.Char(string="目的地")

    _sql_constraints = [
        ("date_check", "CHECK(starttime < endtime)", u'结束时间必须大于出差时间')
    ]