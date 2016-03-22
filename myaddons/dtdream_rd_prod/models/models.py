# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_rd_prod(models.Model):
    _name = 'dtdream_rd_prod.dtdream_rd_prod'
    name = fields.Char("项目名称")
    code = fields.Char("项目编码")


class dtdream_prod_appr(models.Model):
    _name = 'dtdream_rd_prod.dtdream_prod_appr'
    department = fields.Many2one('hr.department','部门')
    department_2 = fields.Many2one('hr.department','二级部门')
    name=fields.Char('产品名称',required=True)
    # code = fields.Char('项目编码')
    state = fields.Char('产品状态')
    version_ids = fields.One2many('dtdream_rd_prod.dtdream_rd_version','pro_id','版本')
    role_ids = fields.Many2many('dtdream_rd_prod.dtdream_rd_config','pro_id','角色')


#部门的联动
    @api.onchange('department_2')
    def _chang_department(self):
        if self.department_2:
            self.department = self.department_2.parent_id

    @api.onchange('department')
    def _chang_department_2(self):
        domain = {}
        if self.department:
            if self.department.child_ids:
                domain['department_2'] = [('parent_id', '=', self.department.id)]
        else:
            domain['department_2'] = [('parent_id.parent_id.parent_id', '=', False)]
        return {'domain': domain}



class dtdream_rd_version(models.Model):
    _name = 'dtdream_rd_prod.dtdream_rd_version'
    proName = fields.Char('产品名称')
    version_numb = fields.Char("版本号")
    pro_flag = fields.Selection([('flag_01','内部测试版本'),('flag_02','外部测试版本'),('flag_03','公测版本'),
                                ('flag_004','演示版本'),('flag_05','补丁版本'),('flag_06','正式版本')],
                             '产品标识')
    version_state = fields.Selection([
        ('initialization','初始化'),
        ('Development','开发中'),
        ('pending','待发布'),
        ('released','已发布')],
        '版本状态')
    plan_dev_time = fields.Date("计划开发时间")
    plan_pub_time = fields.Date("计划发布时间")
    actual_dev_time = fields.Date("实际开发时间")
    actual_pub_time = fields.Date("实际发布时间")
    place = fields.Char('版本存放位置')
    Material =fields.Char('发布材料')
    pro_id = fields.Many2one("dtdream_rd_prod.dtdream_prod_appr")

class dtdream_rd_config(models.Model):
    _name = 'dtdream_rd_prod.dtdream_rd_config'
    name = fields.Char('角色名称')
    pro_id = fields.Many2one("dtdream_rd_prod.dtdream_prod_appr")
    person = fields.Many2one("res.partner",'人员')
