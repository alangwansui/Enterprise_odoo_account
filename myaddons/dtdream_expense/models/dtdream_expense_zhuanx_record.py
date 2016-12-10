# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime, time
from openerp .exceptions import ValidationError,Warning

class dtdream_expense_zhuanx_record(models.Model):
    _name = 'dtdream.expense.zhuanx.record'
    _description = u'专项费用明细'

    # baoxiao_ids = fields.Many2many('dtdream.expense.report', 'aaa')
    fee_type = fields.Char(string='费用类别')
    fee_amount = fields.Integer(string='金额（元）')
    fee_description = fields.Char(string='费用事项说明')