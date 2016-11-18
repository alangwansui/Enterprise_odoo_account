# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime,time
from openerp .exceptions import ValidationError,Warning
import time


import logging
_logger = logging.getLogger(__name__)



#费用明细模型
class dtdream_expense_detail(models.Model):
    _name = "dtdream.expense.detail"

    name = fields.Char(string="名称",required=True)
    parentid = fields.Many2one("dtdream.expense.catelog",string="费用类别",required=True)
    account = fields.Char(string="会计科目")
    account_name = fields.Char(string="会计科目名称")

    @api.multi
    @api.depends('parentid','name')
    def name_get(self):
        result = []
        for detail in self:
            name = detail.parentid.name+'-'+detail.name
            result.append((detail.id, name))
        return result

    # 可以根据费用类别和费用明细查询
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, ['|',('name', 'ilike', name),('parentid', 'ilike', name),] + args, limit=limit)
        return super(dtdream_expense_detail, self).name_search(
            cr, user, '', args=[('id', 'in', list(ids))],
            operator='ilike', context=context, limit=limit)

    _sql_constraints = [

        ('name_unique',
         'UNIQUE(name)',
         "名称不能重复，请重新输入！"),
    ]