# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_reserve_fund_config(models.Model):
    _name = 'dtdream.reserve.fund.config'
    _description = u'备用金费用明细配置'

    name = fields.Char(string='费用类别/科目')
    account = fields.Char(string='科目编码')
    pay_to_who = fields.Selection([(u'付款给员工', '付款给员工'), (u'付款给供应商', '付款给供应商')], string='支付类别')
