# -*- coding: utf-8 -*-

import openerp
from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from lxml import etree
from dateutil.relativedelta import relativedelta
from babel.dates import format_datetime, format_date
import time

#部门权签人设置
class dtdream_informati_security_depart(models.Model):
    _inherit = 'hr.department'
    name=fields.Char()
    # xinxianquanyuan=fields.Many2one("hr.employee",string="信息安全员")
    xinxianquanyuan_new = fields.Many2many("hr.employee", string="信息安全员")