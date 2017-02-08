# -*- coding: utf-8 -*-
from openerp import models, fields, api


#风险类别
class dtdream_rd_risksortconfig(models.Model):
    _name = 'dtdream_rd_risksortconfig'

    name = fields.Char('风险类别', required=True)
