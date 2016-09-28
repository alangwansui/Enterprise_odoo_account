# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime,time
from openerp .exceptions import ValidationError,Warning
import time


import logging
_logger = logging.getLogger(__name__)




class dtdream_expense_benefitdep(models.Model):
    _name = "dtdream.expense.benefitdep"

    @api.depends('name')
    def _compute_department_fields(self):
        for rec in self:
            rec.depcode = rec.name.code

    name = fields.Many2one('hr.department',string="受益部门名称",default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).department_id)
    depcode= fields.Char(string="受益部门编码",compute=_compute_department_fields)
    sharepercent = fields.Char(string="分摊比例(%)",default=100)
    report_id = fields.Many2one("dtdream.expense.report",string="报销单ID")
