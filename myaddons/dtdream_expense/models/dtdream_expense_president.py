# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime,time
from openerp .exceptions import ValidationError,Warning
import time


import logging
_logger = logging.getLogger(__name__)


#公司总裁配置
class dtdream_expense_president(models.Model):
    _name = "dtdream.expense.president"

    name = fields.Many2one("hr.employee",string="姓名")
    type = fields.Selection([('zongcai','总裁'),('fuzongcai','副总裁')])


