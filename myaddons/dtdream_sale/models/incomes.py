# -*- coding: utf-8 -*-

from openerp import models, fields, api

class incomes_inherit_crm_lead(models.Model):
    _inherit = "crm.lead"

    def _compute_cash_sum(self):
        sum = 0
        for rec in self.env['cash.income'].search([('cash_project_id.id','=',self.id)]):
            sum = sum + rec.name
        self.sum_of_cash_income = sum
        self.sum_of_cash_income_store = sum

    def _compute_gaap_sum(self):
        sum = 0
        for rec in self.env['gaap.income'].search([('gaap_project_id.id','=',self.id)]):
            sum = sum + rec.name
        self.sum_of_gaap_income = sum
        self.sum_of_gaap_income_store = sum

    def _compute_contract_sum(self):
        sum = 0
        for rec in self.env['contract.fee'].search([('contract_project_id.id','=',self.id)]):
            sum = sum + rec.name
        self.sum_of_contract_fee = sum
        self.sum_of_contract_fee_store = sum

    def _compute_pay_sum(self):
        sum = 0
        for rec in self.env['fee.pay'].search([('pay_project_id.id','=',self.id)]):
            sum = sum + rec.name
        self.sum_of_fee_pay = sum
        self.sum_of_fee_pay_store = sum

    # 现金收入总额
    sum_of_cash_income = fields.Float('总额(万元)',digits=(16,2),compute=_compute_cash_sum)
    sum_of_cash_income_store = fields.Float('现金收入总额(万元)',digits=(16,2))
    # GAAP收入总额
    sum_of_gaap_income = fields.Float('总额(万元)',digits=(16,2),compute=_compute_gaap_sum)
    sum_of_gaap_income_store = fields.Float('GAAP收入总额(万元)',digits=(16,2))
    # 合同额总额
    sum_of_contract_fee = fields.Float('总额(万元)',digits=(16,2),compute=_compute_contract_sum)
    sum_of_contract_fee_store = fields.Float('合同额总额(万元)',digits=(16,2))
    # 费用支出总额
    sum_of_fee_pay = fields.Float('总额(万元)',digits=(16,2),compute=_compute_pay_sum)
    sum_of_fee_pay_store = fields.Float('费用支出总额(万元)',digits=(16,2))