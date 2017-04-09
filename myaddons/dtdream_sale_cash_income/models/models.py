# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_sale_cash_income(models.Model):
    _name = 'dtdream.sale.cash.income'

    name = fields.Char(default='回款',digits=(16,2))
    cash_date = fields.Date(string="回款日期",required=True)
    cash_partner = fields.Char(string="客户名称",required=True)
    cash_partner_num = fields.Char(string="客户编码",required=True)
    cash_project_id = fields.Many2one("crm.lead",string="项目名称",required=True)
    cash_contract_num = fields.Char(string="合同编号",required=True)
    cash_order_num = fields.Char(string="一级订单号",required=True)
    cash_income = fields.Float(string='回款金额(万元)',required=True)
    cash_type = fields.Char(string="回款类型",required=True)
    cash_type = fields.Selection([
        ('normal', '正常'),
        ('virtual', '总代虚拟'),
    ],required=True,string="回款类型")
    cash_remark = fields.Text(string="备注")

class cash_inherit_crm_lead(models.Model):
    _inherit = 'crm.lead'

    def _compute_cash_sum(self):
        sum = 0
        for rec in self.env['dtdream.sale.cash.income'].search([('cash_project_id.id','=',self.id)]):
            sum = sum + rec.cash_income
        self.sum_of_cash_income = sum
        self.sum_of_cash_income_store = sum

    # 现金收入总额
    sum_of_cash_income = fields.Float('总额(万元)',digits=(16,2),compute=_compute_cash_sum)
    sum_of_cash_income_store = fields.Float('现金收入总额(万元)',digits=(16,2))
