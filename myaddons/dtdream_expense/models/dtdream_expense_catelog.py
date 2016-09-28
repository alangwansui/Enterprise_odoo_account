# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime,time
from openerp .exceptions import ValidationError,Warning
import time


import logging
_logger = logging.getLogger(__name__)





#费用类别模型
class dtdream_expense_catelog(models.Model):
    _name = "dtdream.expense.catelog"

    name = fields.Char(string="名称",required=True)

    _sql_constraints = [

        ('name_unique',
         'UNIQUE(name)',
         "名称不能重复，请重新输入！"),
    ]

