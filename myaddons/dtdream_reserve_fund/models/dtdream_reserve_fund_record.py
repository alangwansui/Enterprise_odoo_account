# -*- coding: utf-8 -*-
from datetime import datetime
from openerp .exceptions import ValidationError
from openerp import models, fields, api


class dtdream_reserve_fund_record(models.Model):
    _name = 'dtdream.reserve.fund.record'
    _description = u'备用金费用明细'

    name = fields.Many2one('dtdream.reserve.fund.config', string='费用类别')
    pay_time = fields.Date(string='要求支付时间', default=datetime.today())
    estimate_amount = fields.Float(string='预估金额')
    reserve_fund_id = fields.Many2one('dtdream.reserve.fund', string='备用金')
    pay_to_who = fields.Char(string='支付类别')

    @api.onchange('estimate_amount')
    def re_compute_total_amount(self):
        if self.reserve_fund_id:
            self.reserve_fund_id.compute_total_amount()

    @api.constrains('name')
    @api.onchange('name')
    def get_pay_to_who(self):
        self.pay_to_who = self.name.pay_to_who


