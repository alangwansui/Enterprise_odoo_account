# -*- coding: utf-8 -*-

from openerp import models, fields, api

# GAAP收入类
class gaap_income(models.Model):
    _name = "gaap.income"

    gaap_date = fields.Datetime(string="GAAP收入确认日期")
    gaap_partner = fields.Char(string="客户名称")
    gaap_partner_num = fields.Char(string="客户编码")
    gaap_project = fields.Char(sring="项目名称")
    gaap_contract_num = fields.Char(string="合同编号")
    gaap_order_num = fields.Char(string="一级订单号")

    gaap_product_line = fields.One2many('gaap.product.line', 'gaap_product_line_id', string='产品列表')

    gaap_income = fields.Float('GAAP收入(万元)',digits=(16,2))

    gaap_project_id = fields.Many2one("crm.lead",string="GAAP收入对应项目")

class gaap_product_line(models.Model):
    _name = 'gaap.product.line'

    gaap_product_line_id = fields.Many2one('gaap.income', string='产品', required=True, ondelete='cascade', index=True, copy=False)

    bom = fields.Char('BOM')
    pro_name = fields.Char('产品型号')
    pro_num = fields.Integer('数量')
    pro_uom_name = fields.Char('单位')
    pro_tax = fields.Char('税率（%）')
    pro_remark1 = fields.Text(string="备注1")
    pro_remark2 = fields.Text(string="备注2")
    pro_remark3 = fields.Text(string="备注3")
    pro_remark4 = fields.Text(string="备注4")
    pro_remark5 = fields.Text(string="备注5")