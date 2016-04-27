# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_resume(models.Model):
    _inherit = 'hr.employee'

    work_address = fields.Char(string="工作常住地")