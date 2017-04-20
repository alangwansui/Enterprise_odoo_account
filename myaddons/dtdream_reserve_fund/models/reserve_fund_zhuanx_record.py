# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions


class reserve_fund_zhuanx_record(models.Model):
    _name = 'reserve.fund.zhuanx.record'
    _description = u'备用金专项费用明细'

    fee_type = fields.Char(string='费用类别')
    fee_amount = fields.Integer(string='金额（元）')
    fee_description = fields.Char(string='费用事项说明')