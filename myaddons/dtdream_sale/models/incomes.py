# -*- coding: utf-8 -*-

from openerp import models, fields, api

class incomes_inherit_crm_lead(models.Model):
    _inherit = "crm.lead"

    def _compute_pay_sum(self):
        sum = 0
        for rec in self.env['fee.pay'].search([('pay_project_id.id','=',self.id)]):
            sum = sum + rec.name
        self.sum_of_fee_pay = sum
        self.sum_of_fee_pay_store = sum

    # 费用支出总额
    sum_of_fee_pay = fields.Float('总额(万元)',digits=(16,2),compute=_compute_pay_sum)
    sum_of_fee_pay_store = fields.Float('费用支出总额(万元)',digits=(16,2))