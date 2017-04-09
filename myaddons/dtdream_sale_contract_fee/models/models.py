# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_sale_contract_fee(models.Model):
    _name = 'dtdream.sale.contract.fee'

    name = fields.Char(default="合同")
    contract_pro_number = fields.Char(string='项目编号',required=True)
    contract_order_date = fields.Date(string="下单日期",required=True)
    contract_partner = fields.Char(string="签单客户",required=True)
    contract_partner_num = fields.Char(string="客户编码",required=True)
    contract_project_id = fields.Many2one("crm.lead",string="项目名称",required=True)
    contract_num = fields.Char(string="合同编号",required=True)
    contract_order_num = fields.Char(string="一级订单号",required=True)
    contract_order_two_num = fields.Char(string="二级订单号",required=True)
    contract_pro_sum = fields.Float(string="产品金额(万元)",required=True)
    contract_yunbao_fee = fields.Float(string="运保费",required=True)
    contract_order_fee = fields.Float(string="订单金额(万元)",required=True)
    contract_sale_fee = fields.Float(string="销售金额(万元)",required=True)
    contract_sale_type = fields.Char(string="销售类型",required=True)
    contract_order_type = fields.Char(string="订单类型",required=True)
    contract_old_order_number = fields.Char(string="原订单号",required=True)
    contract_pry_type = fields.Char(string="付款方式",required=True)
    contract_require_goods_date = fields.Date(string="要货日期",required=True)
    contract_delivery_type = fields.Char(string="交货方式",required=True)
    contract_delivery_address = fields.Char(string="交货地址",required=True)
    contract_receiver = fields.Char(string="签收人",required=True)
    contract_contact_type = fields.Char(string="联系方式",required=True)
    contract_trade_clause = fields.Text(string="贸易条款",required=True)
    contract_remark = fields.Text(string="备注")

class contract_inherit_crm_lead(models.Model):
    _inherit = 'crm.lead'

    def _compute_contract_sum(self):
        sum = 0
        for rec in self.env['dtdream.sale.contract.fee'].search([('contract_project_id.id','=',self.id)]):
            sum = sum + rec.contract_pro_sum
        self.sum_of_contract_fee = sum
        self.sum_of_contract_fee_store = sum

    # 合同额总额
    sum_of_contract_fee = fields.Float('总额(万元)',digits=(16,2),compute=_compute_contract_sum)
    sum_of_contract_fee_store = fields.Float('合同额总额(万元)',digits=(16,2))