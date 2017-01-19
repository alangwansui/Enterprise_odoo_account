# -*- coding: utf-8 -*-
from openerp import models, fields, api

# 审批记录
class chengben_detail_line(models.Model):
    _name = "chengben.detail.line"

    pro_source = fields.Char("来源")
    pro_cost_price = fields.Char("成本(万元)")
    pro_apply_price = fields.Text("申请价(万元)")
    pro_gross_profit = fields.Char("毛利(%)")
    chengben_report_id = fields.Many2one("dtdream.sale.business.report",string="成本明细")