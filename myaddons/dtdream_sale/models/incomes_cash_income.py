# -*- coding: utf-8 -*-

from openerp import models, fields, api

# 现金收入类
class cash_income(models.Model):
    _name = "cash.income"

    name = fields.Float('现金收入(万元)',digits=(16,2))
    cash_project_id = fields.Many2one("crm.lead",string="现金收入对应项目")