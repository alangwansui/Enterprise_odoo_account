# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError

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

    state = fields.Selection([('state_00','初始化'),('state_01','立项'),('state_02','总体设计'),('state_03','迭代开发'),('state_04','验证发布'),('state_05','结束')],'产品状态',readonly=True,default='state_00')

    # state_id = fields.Many2one('dtdream_rd_prod.state','产品状态', track_visibility='onchange')

    version_ids = fields.One2many('dtdream_rd_prod.dtdream_rd_version','proName','版本')
    role_ids = fields.Many2many('dtdream_rd_prod.dtdream_rd_config','pro_id','角色')

    pro_time = fields.Date('立项时间')
    overall_plan_time = fields.Date('总体设计计划开始时间')
    overall_actual_time = fields.Date('总体设计实际开始时间')

    start_pro_mar = fields.Text('立项材料')
    overall_mar = fields.Text('总体设计材料')


    color = fields.Integer('Color Index')
    active = fields.Boolean(default=True)

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
                self.department_2 =  self.department.child_ids[0]
                domain['department_2'] = [('parent_id', '=', self.department.id)]
        else:
            domain['department_2'] = [('parent_id.parent_id', '=', False)]
        return {'domain': domain}

    # @api.model
    # def create(self, vals):         #创建研发项目时，会计项目添加记录
    #     result = super(dtdream_prod_appr, self).create(vals)
    #     pro={}
    #     pro['name']=vals['name']
    #     pro['code']='0001'
    #     self.env['dtdream_rd_prod.dtdream_rd_prod'].create(pro)
    #     return result

    @api.model
    def wkf_draft(self):
        self.write({'state': 'state_00'})

    @api.multi
    def wkf_lixiang(self):
        lg = len(self.version_ids)
        if lg<=0:
            raise ValidationError("提交项目时必须至少有一个版本")
        self.write({'state': 'state_01'})

    @api.multi
    def wkf_ztsj(self):
        self.write({'state': 'state_02'})

    @api.multi
    def wkf_ddkf(self):
        self.write({'state': 'state_03'})

    @api.multi
    def wkf_yzfb(self):
        versions = self.version_ids
        # for version in versions:
            # if version.version_state =='initialization' or version.version_state =='Development':
        self.write({'state': 'state_04'})

    @api.multi
    def wkf_jieshu(self):
        self.write({'state': 'state_05'})


class dtdream_rd_version(models.Model):
    _name = 'dtdream_rd_prod.dtdream_rd_version'
    version_numb = fields.Char("版本号",required=True)
    @api.onchange('proName')
    def _get_pro(self):
        self.name = self.proName.name
        # self.proState = self.proName.state

    name=fields.Char()
    # proState = fields.Char()
    proName = fields.Many2one("dtdream_rd_prod.dtdream_prod_appr" ,string='产品名称',required=True)


    pro_flag = fields.Selection([('flag_06','正式版本'),('flag_01','内部测试版本'),('flag_02','外部测试版本'),('flag_03','公测版本'),
                                ('flag_04','演示版本'),('flag_05','补丁版本')],
                             '版本标识')
    version_state = fields.Selection([
        ('initialization','初始化'),
        ('Development','开发中'),
        ('pending','待发布'),
        ('released','已发布')],
        '版本状态',default="initialization")
    plan_dev_time = fields.Date("计划开发开始时间",help="版本开始时间指迭代开发开始时间")
    plan_check_pub_time = fields.Date("计划验证发布开始时间")
    plan_pub_time = fields.Date("计划发布完成时间")
    plan_mater=fields.Text("版本计划材料")

    actual_dev_time = fields.Date("实际开发开始时间",help="版本开始时间指迭代开发开始时间")
    dev_mater = fields.Text("版本开发材料")

    actual_check_pub_time =fields.Date("实际验证发布开始时间")
    actual_pub_time = fields.Date("实际发布完成时间")
    place = fields.Char('版本存放位置')
    Material =fields.Text('版本发布材料')


    @api.model
    def wkf_draft(self):
        self.write({'version_state': 'initialization'})

    @api.model
    def wkf_kaifa(self):
        self.write({'version_state': 'Development'})

    @api.model
    def wkf_dfb(self):
        self.write({'version_state': 'pending'})

    @api.model
    def wkf_yfb(self):
        self.write({'version_state': 'released'})



class dtdream_rd_config(models.Model):
    _name = 'dtdream_rd_prod.dtdream_rd_config'
    name = fields.Char('角色名称')
    pro_id = fields.Many2one("dtdream_rd_prod.dtdream_prod_appr")
    person = fields.Many2one("hr.employee",'人员')


# class dtdream_rd_prod_state(models.Model):
#     _name = 'dtdream_rd_prod.state'
#     name=fields.Char('名称')