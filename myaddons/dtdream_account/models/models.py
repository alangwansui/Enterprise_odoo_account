# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_account(models.Model):
    _inherit = 'account.account.type'

    type = fields.Selection([
        ('other', 'Regular'),
        ('receivable', 'Receivable'),
        ('payable', 'Payable'),
        ('liquidity', 'Liquidity'),
        ('account_type_0', '非流动负债'),
        ('account_type_1', '非流动资产'),
        ('account_type_2', '流动负债'),
        ('account_type_3', '流动资产'),
        ('account_type_4', '所有者权益'),
        ('account_type_5', '财务费用'),
        ('account_type_6', '期间费用'),
        ('account_type_7', '所得税费用'),
        ('account_type_8', '投资收益'),
        ('account_type_9', '营业外收入'),
        ('account_type_10', '营业外支出'),
        ('account_type_11', '营业务成本'),
        ('account_type_12', '营业务收入'),
        ('account_type_13', '营业务税金及附加'),
        ('account_type_14', '资本公积'),
    ], required=True,
        help="The 'Internal Type' is used for features available on "\
        "different types of accounts: liquidity type is for cash or bank accounts"\
        ", payable/receivable is for vendor/customer accounts.")
    # note = fields.Text(string='说明12222')
#     _name = 'dtdream_account.dtdream_account'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100