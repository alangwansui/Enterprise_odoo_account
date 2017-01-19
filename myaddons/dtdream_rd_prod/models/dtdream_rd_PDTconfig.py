# -*- coding: utf-8 -*-
from openerp import models, fields, api


#产品里的PDT
class dtdream_rd_PDTconfig(models.Model):
    _name = 'dtdream.rd.pdtconfig'

    name = fields.Char('PDT名称', required=True)
    department = fields.Many2one('hr.department', '部门', required=True)