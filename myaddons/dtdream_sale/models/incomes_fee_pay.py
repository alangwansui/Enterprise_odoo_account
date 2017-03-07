# -*- coding: utf-8 -*-

from openerp import models, fields, api

# 费用支出类
class fee_pay(models.Model):
    _name = "fee.pay"

    name = fields.Float('费用支出(万元)',digits=(16,2))
    pay_project_id = fields.Many2one("crm.lead",string="费用支出对应项目")