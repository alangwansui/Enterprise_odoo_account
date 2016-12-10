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


    # 可以根据费用类别和费用明细查询
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        employee_id = self.pool.get('hr.employee').search(cr,user,[('user_id','=',user)])
        if self.pool.get('hr.employee').browse(cr, user,employee_id,context=context).travel_grant:
            ids = self.search(cr, user, [('name', 'ilike', name),('name', '!=', u"市内交通费")] + args, limit=limit)
        else:
            ids = self.search(cr, user, [('name', 'ilike', name)] + args, limit=limit)
        return super(dtdream_expense_detail, self).name_search(
            cr, user, '', args=[('id', 'in', list(ids))],
            operator='ilike', context=context, limit=limit)

    _sql_constraints = [

        ('name_unique',
         'UNIQUE(name)',
         "名称不能重复，请重新输入！"),
    ]