# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_hr(models.Model):
    _inherit = 'hr.department'

    code = fields.Char("部门编码")
    assitant_id = fields.Many2many("hr.employee",string="行政助理")


class dtdream_hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.depends("travel_ids")
    def _compute_chucha_log(self):
        cr = self.env["dtdream.travel.chucha"].search([("name.id", "=", self.id)])
        self.chucha_log_nums = len(cr)

    @api.depends("hr_bussiness")
    def _compute_hr_business_log(self):
        cr = self.env["dtdream_hr_business.dtdream_hr_business"].search([("name.id", "=", self.id)])
        self.hr_business_log_nums = len(cr)

    @api.depends("hr_holiday")
    def _compute_hr_holiday_log(self):
        cr = self.env["hr.holidays"].search([("employee_id", "=", self.id)])
        self.hr_holiday_log_nums = len(cr)

    @api.one
    def _compute_has_view(self):
        if self.user_id == self.env.user or self.env.user.id == 1:
            self.can_view = True
        else:
            self.can_view = False

    full_name = fields.Char(string="姓名")
    can_view = fields.Boolean(compute= "_compute_has_view")
    gender = fields.Selection([('male', '男'), ('female', '女')], '性别')
    job_number = fields.Char("工号")
    home_address = fields.Char("居住地址")
    education = fields.Selection([
        ('education_01', '中专'),
        ('education_02','大专'),
        ('education_03','本科'),
        ('education_04', '硕士'),
        ('education_05', '博士'),
        ('education_06', '其他'),
        ], string='最高学历')

    duties = fields.Char("职务")
    post = fields.Char("岗位")
    Inaugural_state = fields.Selection([('Inaugural_state_01','在职'),('Inaugural_state_02','离职')],"就职状态")
    entry_day=fields.Date("入职日期")
    travel_ids = fields.One2many("dtdream.travel.chucha", "employ", string="出差")
    chucha_log_nums = fields.Integer(compute='_compute_chucha_log', string="出差记录")
    hr_bussiness = fields.One2many("dtdream_hr_business.dtdream_hr_business", "employ", string="外出公干")
    hr_business_log_nums = fields.Integer(compute='_compute_hr_business_log', string="外出公干记录")
    hr_holiday = fields.One2many("hr.holidays", "log", string="休假")
    hr_holiday_log_nums = fields.Integer(compute='_compute_hr_holiday_log', string="休假记录")



