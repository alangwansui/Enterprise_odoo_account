# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_hr(models.Model):
    _inherit = 'hr.department'



class dtdream_hr_employee(models.Model):
    _inherit = 'hr.employee'

    full_name = fields.Char(string="姓名")
    gender = fields.Selection([('male', '男'), ('female', '女')], '性别')
    job_number = fields.Char("工号")
    home_address = fields.Char("居住地址")
    education = fields.Selection([
        ('education_01', '中专'),
        ('education_02','大专'),
        ('education_03','本科'),
        ('education_04', '硕士'),
        ('education_05', '博士'),
        ('education_05', '其他'),
        ], string='最高学历')

    duties = fields.Char("职务")
    post = fields.Char("岗位")
    Inaugural_state = fields.Selection([('Inaugural_state_01','在职'),('Inaugural_state_02','离职')],"就职状态")
    entry_day=fields.Date("入职日期")

