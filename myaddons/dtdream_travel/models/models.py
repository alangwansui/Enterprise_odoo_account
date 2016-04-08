# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_travel(models.Model):
    _name = 'dtdream.travel.chucha'
    _inherit = ['mail.thread']

    @api.depends('traveling_fee', 'incity_fee', 'hotel_expense', 'other_expense')
    def _compute_expense_total(self):
        for rec in self:
            rec.total = rec.traveling_fee + rec.incity_fee + rec.hotel_expense + rec.other_expense

    @api.one
    def _compute_is_shenpiren(self):
        if self.shenpi_first == self.env.user and self.state == "1":
            self.is_shenpiren = True
        elif self.shenpi_second == self.env.user and self.state == "2":
            self.is_shenpiren = True
        elif self.shenpi_third == self.env.user and self.state == "3":
            self.is_shenpiren = True
        elif self.shenpi_fourth == self.env.user and self.state == "4":
            self.is_shenpiren = True
        elif self.shenpi_fifth == self.env.user and self.state == "5":
            self.is_shenpiren = True
        else:
            self.is_shenpiren = False

    @api.onchange("shenpi_second")
    @api.constrains("shenpi_second")
    def check_shenpi_first(self):
        if not self.shenpi_first.id and self.shenpi_second.id:
            self.shenpi_second = False
            warning = {
                'title': '提示',
                'message': '审批人必须按顺序填写!',
            }
            return {'warning': warning}

    @api.onchange("shenpi_third")
    @api.constrains("shenpi_third")
    def check_shenpi_second(self):
        if not self.shenpi_second.id and self.shenpi_third.id:
            self.shenpi_third = False
            warning = {
                'title': '提示',
                'message': '审批人必须按顺序填写!',
            }
            return {'warning': warning}

    @api.onchange("shenpi_fourth")
    @api.constrains("shenpi_fourth")
    def check_shenpi_third(self):
        if not self.shenpi_third.id and self.shenpi_fourth.id:
            self.shenpi_fourth = False
            warning = {
                'title': '提示',
                'message': '审批人必须按顺序填写!',
            }
            return {'warning': warning}

    @api.onchange("shenpi_fifth")
    @api.constrains("shenpi_fifth")
    def check_shenpi_fourth(self):
        if not self.shenpi_fourth.id and self.shenpi_fifth.id:
            self.shenpi_fifth = False
            warning = {
                'title': '提示',
                'message': '审批人必须按顺序填写!',
            }
            return {'warning': warning}

    @api.multi
    def unlink(self):
        # from openerp.exceptions import ValidationError
        # raise ValidationError("12333333333333333333")
        warning = {
                'title': '提示',
                'message': '审批人必须按顺序填写!',
         }
        return {'warning': warning}


    name = fields.Char(string="申请人", default=lambda self: self.env["hr.employee"].search(
        [("login", "=", self.env.user.login)]).name, readonly=True)
    shenpi_first = fields.Many2one('res.users', string="第一审批人", help="部门行政助理", required=True,
        default=lambda self: self.env["dtdream.travel.chucha"].search([("create_uid", "=", self.env.user.login)], limit=1, order="id desc").shenpi_first)
    shenpi_second = fields.Many2one('res.users', string="第二审批人", help="部门主管",
        default=lambda self: self.env["dtdream.travel.chucha"].search([("create_uid", "=", self.env.user.login)], limit=1, order="id desc").shenpi_second)
    shenpi_third = fields.Many2one('res.users', string="第三审批人", help="受益部门权签人(当受益部门与权签部门不一致时)",
        default=lambda self: self.env["dtdream.travel.chucha"].search([("create_uid", "=", self.env.user.login)], limit=1, order="id desc").shenpi_third)
    shenpi_fourth = fields.Many2one('res.users', string="第四审批人",
        default=lambda self: self.env["dtdream.travel.chucha"].search([("create_uid", "=", self.env.user.login)], limit=1, order="id desc").shenpi_fourth)
    shenpi_fifth = fields.Many2one('res.users', string="第五审批人",
        default=lambda self: self.env["dtdream.travel.chucha"].search([("create_uid", "=", self.env.user.login)], limit=1, order="id desc").shenpi_fifth)
    shenpiren = fields.Many2one('res.users', string="是否当前审批人")
    is_shenpiren = fields.Boolean(compute=_compute_is_shenpiren, string="是否审批人")
    workid = fields.Char(string="工号", readonly=True, default=lambda self: self.env["hr.employee"].search(
        [("login", "=", self.env.user.login)]).job_number)
    deperment = fields.Char(string="部门", readonly=True, default=lambda self: self.env["hr.employee"].search(
        [("login", "=", self.env.user.login)]).department_id.name)
    create_time = fields.Datetime(string="创建时间", default=fields.Datetime.now)
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
         ('99', '结束')], string="状态", default="0")

    @api.multi
    def wkf_draft(self):
        self.write({'state': '0', "shenpiren": ''})

    @api.multi
    def wkf_approve1(self):
        self.shenpiren = self.shenpi_first
        self.write({'state': '1'})

    @api.multi
    def wkf_approve2(self):
        if self.shenpi_second.id:
            self.shenpiren = self.shenpi_second
            self.write({'state': '2'})
        else:
            self.write({'state': '99', "shenpiren": ''})

    @api.multi
    def wkf_approve3(self):
        if self.shenpi_third.id:
            self.shenpiren = self.shenpi_third
            self.write({'state': '3'})
        else:
            self.write({'state': '99', "shenpiren": ''})

    @api.multi
    def wkf_approve4(self):
        if self.shenpi_fourth.id:
            self.shenpiren = self.shenpi_fourth
            self.write({'state': '4'})
        else:
            self.write({'state': '99', "shenpiren": ''})

    @api.multi
    def wkf_approve5(self):
        if self.shenpi_fifth.id:
            self.shenpiren = self.shenpi_fifth
            self.write({'state': '5'})
        else:
            self.write({'state': '99', "shenpiren": ''})

    @api.multi
    def wkf_done(self):
        self.shenpiren = False
        self.write({'state': '99'})


class dtdream_travel_journey(models.Model):
    _name = "dtdream.travel.journey"

    travel_id = fields.Many2one("dtdream.travel.chucha", string="申请人")
    name = fields.Char(related="travel_id.name", string="姓名")
    starttime = fields.Date(default=fields.Date.today, string="出差时间")
    endtime = fields.Date(string="结束时间")
    startaddress = fields.Char(string="出发地")
    endaddress = fields.Char(string="目的地")
    reason = fields.Text(string="出差原因")

    _sql_constraints = [
        ("date_check", "CHECK(starttime < endtime)", u'结束时间必须大于出差时间')
    ]