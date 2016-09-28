# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime,time
from openerp .exceptions import ValidationError,Warning
import time


import logging
_logger = logging.getLogger(__name__)



class dtdream_expense_city(models.Model):
    _name = "dtdream.expense.city"

    name = fields.Char(string="城市")
    provinceid = fields.Many2one("res.country.state",string="所属省份")