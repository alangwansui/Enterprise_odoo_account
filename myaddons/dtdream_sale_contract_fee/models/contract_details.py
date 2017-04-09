# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_sale_contract_details(models.Model):
    _name = 'dtdream.sale.contract.details'

    @api.depends('details_pro_list_price','details_pro_discount')
    def _compute_apply_price(self):
        self.details_pro_apply_price = self.details_pro_list_price * self.details_pro_discount / 100.0

    @api.depends('details_pro_apply_price','details_pro_num')
    def _compute_pro_sum(self):
        self.details_pro_sum = self.details_pro_apply_price * self.details_pro_num

    @api.depends('details_pro_apply_price','details_pro_num_by_two')
    def _compute_pro_sum_two(self):
        self.details_pro_sum_two = self.details_pro_apply_price * self.details_pro_num_by_two

    name = fields.Char(default="合同明细")
    details_order_date = fields.Date(string="下单日期",required=True)
    details_project_id = fields.Many2one("crm.lead",string="项目名称",required=True)
    details_num = fields.Char(string="合同编号",required=True)
    details_order_num = fields.Char(string="一级订单号",required=True)
    details_order_two_num = fields.Char(string="二级订单号",required=True)
    details_bom = fields.Char(string="bom",required=True)
    details_pro_name = fields.Char('产品型号',required=True)
    details_pro_type = fields.Char('产品类别',required=True)
    details_pro_description = fields.Char('产品描述',required=True)
    details_pro_uom_name = fields.Char('单位',required=True)
    details_pro_supply = fields.Char('供应商',required=True)
    details_pro_list_price = fields.Float('目录价',required=True)
    details_pro_num = fields.Integer('数量',required=True)
    details_pro_num_by_two = fields.Integer('二级渠道出货数量',required=True)
    details_pro_discount = fields.Float('折扣率(%)',required=True)
    details_pro_apply_price = fields.Float('单价',compute=_compute_apply_price)
    details_pro_sum = fields.Float('金额',compute=_compute_pro_sum)
    details_pro_sum_two = fields.Float('二级渠道出货金额',compute=_compute_pro_sum_two)
    details_service_active_date = fields.Date('服务生效日期',required=True)
    details_service_last_days = fields.Integer('服务期限(天)',required=True)
    details_remark = fields.Text('备注')