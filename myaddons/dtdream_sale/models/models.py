# -*- coding: utf-8 -*-

from openerp import models, fields, api

# 继承产品模型，修改字段
class dtdream_sale(models.Model):
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

# 新增产品类别
class product_pro_type(models.Model):
    _name = 'product.pro.type'

    name = fields.Char('产品类别',required=True)