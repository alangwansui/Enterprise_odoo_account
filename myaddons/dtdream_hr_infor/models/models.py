# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_hr_infor(models.Model):
    _inherit = "hr.employee"

    account = fields.Char(string="账号", required=True)
    byname = fields.Char(string="等价花名")
    num = fields.Char(string="工号", required=True)
    recruit = fields.Selection([('0', "社会招聘"), ('1', "校园招聘")], string="招聘类型", required=True)
    work_place = fields.Char(string="常驻工作地", required=True)
    recruit_place = fields.Char(string="招聘所在地", required=True)
    expatriate = fields.Boolean(string="是否外派")
    nation = fields.Char(string="民族", required=True)
    political = fields.Selection([("0", "党员"), ("1", "群众"), ("2", "其它")], string="政治面貌", required=True)
    marry = fields.Selection([("0", "未婚"), ("1", "已婚"), ("2", "离异")], string="婚姻", required=True)
    child = fields.Integer(string="子女数")
    icard = fields.Char(string="身份证", required=True)
    postcode = fields.Char(string="邮编", required=True)
    birthday = fields.Date(string="出生日期", required=True)
    Birthplace = fields.Char(string="籍贯", required=True)
    graduate = fields.Boolean(string="是否应届生")
    family = fields.One2many("hr.employee.family", "employee_id", string="family")
    registered = fields.Many2one("res.country.state", string="省份")


class dtdream_hr_family(models.Model):
    _name = "hr.employee.family"

    employee_id = fields.Many2one("hr.employee", string="employee")
    relation = fields.Char(string="关系", required=True)
    name = fields.Char(string="姓名", required=True)
    company = fields.Char(string="工作单位", required=True)
    address = fields.Char(string="地址", required=True)
    postcode = fields.Char(string="邮编", required=True)
    mail = fields.Char(string="邮箱", required=True)
    tel = fields.Char(string="联系电话", required=True)
    emergency = fields.Boolean(string="紧急联系人")



