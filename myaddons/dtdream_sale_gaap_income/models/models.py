# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_sale_gaap_income(models.Model):
    _name = 'dtdream.sale.gaap.income'

    @api.depends('pro_price','pro_num','pro_tax')
    def _compute_gaap_income(self):
        self.gaap_income = self.pro_price * self.pro_num / (1 + self.pro_tax /100) / 10000

    name = fields.Char(default="GAAP收入")
    gaap_date = fields.Date(string="GAAP收入确认日期",required=True)
    gaap_partner = fields.Char(string="客户名称",required=True)
    gaap_partner_num = fields.Char(string="客户编码",required=True)
    gaap_project_id = fields.Many2one("crm.lead",string="项目名称",required=True)
    gaap_contract_num = fields.Char(string="合同编号",required=True)
    gaap_order_num = fields.Char(string="一级订单号",required=True)
    bom = fields.Char('BOM',required=True)
    pro_name = fields.Char('产品型号',required=True)
    pro_num = fields.Integer('数量',required=True)
    pro_price = fields.Float('单价(元)',required=True)
    pro_tax = fields.Float('税率（%）',required=True)
    gaap_income = fields.Float('GAAP收入(万元)',digits=(16,2),compute=_compute_gaap_income,store=True)
    pro_remark1 = fields.Text(string="备注")
    pro_remark2 = fields.Text(string="备注2")
    pro_remark3 = fields.Text(string="备注3")
    pro_remark4 = fields.Text(string="备注4")
    pro_remark5 = fields.Text(string="备注5")

class gaap_inherit_crm_lead(models.Model):
    _inherit = 'crm.lead'

    def _compute_gaap_sum(self):
        sum = 0
        for rec in self.env['dtdream.sale.gaap.income'].search([('gaap_project_id.id','=',self.id)]):
            sum = sum + rec.gaap_income
        self.sum_of_gaap_income = sum
        self.sum_of_gaap_income_store = sum

    # GAAP收入总额
    sum_of_gaap_income = fields.Float('总额(万元)',digits=(16,2),compute=_compute_gaap_sum)
    sum_of_gaap_income_store = fields.Float('GAAP收入总额(万元)',digits=(16,2))