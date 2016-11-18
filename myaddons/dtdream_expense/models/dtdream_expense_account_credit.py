# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_expense_account_credit(models.Model):
    _name = 'dtdream.expense.account.credit'
    _description = u"贷方会计科目表"

    name = fields.Char()
    paytype = fields.Selection([('yinhangzhuanzhang',u'银行转账'),('hexiaobeiyongjin',u'核销备用金')],string=u"支付方式",required=True)
    paycatelog = fields.Selection([('fukuangeiyuangong',u'付款给员工'),('fukuangeigongyingshang',u'付款给供应商')],string=u"支付类别",required=True)
    account = fields.Char(string='会计科目')
    account_name = fields.Char(string='会计科目名称')

    @api.constrains("account")
    def _compute_name(self):
        self.name = self.account