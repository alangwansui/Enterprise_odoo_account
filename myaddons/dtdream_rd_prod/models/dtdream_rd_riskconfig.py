# -*- coding: utf-8 -*-
from openerp import models, fields, api


#风险状态
class dtdream_rd_riskconfig(models.Model):
    _name = 'dtdream_rd_riskconfig'

    name = fields.Char('风险状态', required=True)
