# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_order(models.Model):
    _name = 'dtdream.project.order'

    code = fields.Char(string='订单编号', size=16)
    order_type = fields.Char(string='订单类型', size=8)
    bom = fields.Char(string='BOM', size=8)
    version = fields.Char(string='型号', size=16)
    product_type = fields.Char(string='产品类别', size=8)
    product_des = fields.Text(string="产品描述")
    company = fields.Char(string='单位', size=16)
    vender = fields.Char(string='生产厂家', size=16)
    num = fields.Integer(string='数量')
    project_manage_id = fields.Many2one('dtdream.project.manage')

    _sql_constraints = [
        ('order_code_uniquee', 'UNIQUE(code)', "订单编号已存在!"),
    ]
