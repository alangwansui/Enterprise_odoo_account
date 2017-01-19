# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class dtdream_information_record(models.Model):
    _name = 'dtdream.information.record'
    _description = u"申请权限记录"

    event = fields.Many2one("dtdream.information.purview",string="申请事项")
    applicant = fields.Many2one("hr.employee",string="申请人")
    ldap_group = fields.Char()
    dead_line = fields.Date()