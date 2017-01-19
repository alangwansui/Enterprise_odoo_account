# -*- coding: utf-8 -*-
from openerp import models, fields, api


#风险类型
class dtdream_rd_riskconfig(models.Model):
    _name = 'dtdream_rd_riskconfig'

    name = fields.Char('风险类型', required=True)
