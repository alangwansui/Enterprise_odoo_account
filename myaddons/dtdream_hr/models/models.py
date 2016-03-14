# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_hr(models.Model):
    _inherit = 'hr.department'



class dtdream_hr_employee(models.Model):
    _inherit = 'hr.employee'

    full_name = fields.Char(string="花名")
    account_number = fields.Char("帐号")
    job_number = fields.Char("工号")
    childrenNumber = fields.Integer("子女数")
    education = fields.Selection([
        ('education_01', '高中'),
        ('education_02','专科'),
        ('education_03','本科'),
        ('education_04', '硕士'),
        ('education_05', '博士'),
        ], string='学历',  default='education_02')

    nation = fields.Char("民族")
    political_statu = fields.Selection([
        ('political_statu_01','群众'),
        ('political_statu_2','党员'),
        ('political_statu_3','共青团员'),
    ])
    zip_code = fields.Char("邮编")
    birthplace = fields.Char("籍贯")
    Job_Type = fields.Char("招聘类型")
    duties = fields.Char("职务")
    post = fields.Char("岗位")
    Inaugural_state = fields.Selection([('Inaugural_state_01','在职'),('Inaugural_state_02','离职')],"就职状态")
    entry_day=fields.Date("入职日期")



    oil_number = fields.Char("油卡编号")
    zhongda = fields.Boolean("中大一卡通")

    family_ids = fields.One2many('hr.employee.family','family_id',"家庭成员")

    Residing = fields.Char("户口所在地")
    Hukou = fields.Selection([
        ('Hukou_01','农村'),
        ('Hukou_02','城镇')],
            "户口性质")
    sb_month= fields.Date("上家单位社保缴纳截至月份")
    gjj_month=fields.Date("上家单位公积金缴纳截至月份")
    sb_add = fields.Char("原社保缴纳地")
    gjj_add = fields.Char("原公积金缴纳地")
    apply_add= fields.Char("申请社保缴纳地")



class employee_family(models.Model):
    _name='hr.employee.family'
    relation = fields.Char("关系")
    name = fields.Char("姓名")
    employer = fields.Char("工作单位")
    zip_code = fields.Char("邮编")
    email = fields.Char("邮箱")
    tel = fields.Char("联系电话")
    eme_cont = fields.Boolean("紧急联系人")

    family_id = fields.Many2one('hr.employee',"员工")

