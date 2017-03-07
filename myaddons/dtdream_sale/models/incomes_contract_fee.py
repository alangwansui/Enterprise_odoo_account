# -*- coding: utf-8 -*-

from openerp import models, fields, api

# 合同额类
class contract_fee(models.Model):
    _name = "contract.fee"

    # @api.depends('contract_project_id')
    # def _get_project_info(self):
    #     for rec in self:
    #         if rec.contract_project_id:
    #             rec.contract_name = rec.contract_project_id.name
    #             rec.contract_categ_id_parent = rec.contract_project_id.
    #             rec.contract_categ_id = rec.contract_project_id.

    contract_project_id = fields.Many2one("crm.lead",string="合同额对应项目")
    contract_sequence_num = fields.Char(string="序号")
    contract_year = fields.Integer(string="年")
    contract_month = fields.Integer(string="月")
    contract_order_date = fields.Date(string="下单日期")
    contract_name = fields.Char(string="项目名称")
    contract_province = fields.Char(string="省份")
    contract_partner = fields.Char(string="客户名称")
    contract_num = fields.Char(string="合同编号")
    contract_order_num = fields.Char(string="一级订单号")
    contract_sale_apply_person = fields.Char(string="营销责任人")
    contract_office = fields.Char(string="办事处")
    contract_system = fields.Char(string="系统部")
    contract_industry = fields.Char(string="行业")
    contract_categ_id_parent = fields.Char(string="产品一级分类")
    contract_categ_id = fields.Char(string="产品二级分类")
    contract_bom = fields.Char(string="bom编码")
    contract_pro_type = fields.Char(string='产品类别')
    contract_pro_description_out = fields.Char(string='产品对外中文描述')
    contract_pro_num = fields.Integer(string='数量')
    contract_total_list_price = fields.Float(string='总目录价',digits=(16,2))
    contract_list_price = fields.Float(string='目录价',digits=(16,2))
    contract_pro_uom_name = fields.Char(string='单位')
    contract_apply_discount = fields.Float(string='申请折扣(%)')
    contract_total_chuhuo_price = fields.Float(string='合同额(万元)',digits=(16,2))
    contract_pro_seller = fields.Char(string="供应商")