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
    province_hukou = fields.Many2one("dtdream.hr.province", required=True)
    state_hukou = fields.Many2one("dtdream.hr.state", required=True)
    nature_hukou = fields.Selection([("0", "城镇"), ("1", "农村")], string="户口性质", required=True)
    endtime_shebao = fields.Date(string="上家单位社保缴纳截止月份", required=True)
    endtime_gongjijin = fields.Date(string="上家单位公积金缴纳截止月份", required=True)
    ahead_prov = fields.Many2one("dtdream.hr.province", required=True)
    ahead_state = fields.Many2one("dtdream.hr.state", required=True)
    now_prov = fields.Many2one("dtdream.hr.province", required=True)
    now_state = fields.Many2one("dtdream.hr.state", required=True)
    shebao_prov = fields.Many2one("dtdream.hr.province", required=True)
    gongjijin_state = fields.Many2one("dtdream.hr.state", required=True)
    oil_card = fields.Char(string="油卡编号")
    has_oil = fields.Boolean(string="已办理中大一卡通")


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


class dtdream_hr_province(models.Model):
    _name = "dtdream.hr.province"

    name = fields.Char(string="省份", required=True)
    code = fields.Char(string="简称")
    state = fields.One2many("dtdream.hr.state", "province", string="市区")

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", u'省份必须是唯一的'),
    ]


class dtdream_hr_state(models.Model):
    _name = "dtdream.hr.state"

    name = fields.Char(string="市区", required=True)
    province = fields.Many2one("dtdream.hr.province", string="省份", required=True)


class dtdream_hr_contract(models.Model):
    _name = "dtdream.hr.contract"

    deperment = fields.Char(string="部门", required=True)
    name = fields.Char(string="花名", required=True)
    num = fields.Char(string="工号", required=True)
    date_start = fields.Date(string="合同开始日期", required=True)
    date_stop = fields.Date(string="合同结束日期", required=True)



