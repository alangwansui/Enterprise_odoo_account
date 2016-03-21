# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime

# 继承产品模型，修改字段
class dtdream_product(models.Model):
    _inherit = ["product.template"]

    bom = fields.Char(string="BOM",required=True)
    pro_status = fields.Selection([
        ('inPro', '生产'),
        ('outPro', '停产'),
    ])
    pro_type = fields.Many2one("product.pro.type", string="产品类别",required=True)

    pro_description = fields.Text(string="产品描述")
    ref_discount = fields.Float(string="参考折扣")
    pro_version = fields.Char(string="版本")
    remark = fields.Text(string="备注")
    office_manager_discount = fields.Float(string="办事处主任授权折扣")
    system_department_discount = fields.Float(string="系统部授权折扣")
    market_president_discount = fields.Float(string="市场部总裁授权折扣")
    company_president_discount = fields.Float(string="公司总裁授权折扣")

# 定义产品类别
class product_pro_type(models.Model):
    _name = 'product.pro.type'

    name = fields.Char('产品类别',required=True)

#定义办事处模型
class dtdream_office(models.Model):
    _name = 'dtdream.office'

    name = fields.Char("办事处名称",required=True)
    code = fields.Char("办事处编码",required=True)

class dtdream_sale(models.Model):
    _inherit = 'crm.lead'

    user_id = fields.Many2one(string="项目责任人")
    project_number = fields.Char(string="项目编号", default="New",store=True,readonly=True)
    project_leave = fields.Selection([
        ('company_leave', '公司级'),
        ('department_leave', '部门级'),
        ('normal_leave', '一般项目'),
    ])

    # sys_department = fields.Many2one("dtdream.industry", string="系统部")
    industry = fields.Many2one("dtdream.industry", string="行业")
    # sub_industry = fields.Many2one("dtdream.industry", string="子行业")
    office = fields.Many2one("dtdream.office", string="办事处",required=True)

    bidding_time = fields.Date("招标时间")
    supply_time = fields.Date("供货时间")
    # project_stage =fields.Selection([
    #     ('point', '机会点'),
    #     ('start', '项目启动'),
    #     ('communication', '商务/技术交流'),
    #     ('bidding', '项目招投标'),
    #     ('end', '项目结束'),
    # ])
    project_detail = fields.Text("项目详情")

    @api.model
    def create(self, vals):
        if vals.get('project_number', 'New') == 'New':
            o_id = vals.get('office')
            office_rec = self.env['dtdream.office'].search([('id','=',o_id)])
            print office_rec.code
            print self.env['ir.sequence'].next_by_code('project.number')
            vals['project_number'] = ''.join([office_rec.code,self.env['ir.sequence'].next_by_code('project.number'),'N']) or 'New'
        result = super(dtdream_sale, self).create(vals)
        return result

# 定义行业模型
class dtdream_industry(models.Model):
    _name = 'dtdream.industry'

    @api.multi
    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res
        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    name = fields.Char(string='行业名称',required=True)
    code = fields.Char(string='行业编码',required=True)
    parent_id = fields.Many2one('dtdream.industry', string='上级行业')
    children_ids = fields.One2many('dtdream.industry','parent_id',string='下级行业')