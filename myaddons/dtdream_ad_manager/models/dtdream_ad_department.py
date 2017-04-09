# -*- coding: utf-8 -*-
from openerp import models, fields


# 域用户信息
class dtdream_ad_department(models.Model):
    _name = 'dtdream.ad.department'
    _description = u'部门缩写'

    name = fields.Many2one('hr.department', string=u'部门', required=True)
    value = fields.Char(string=u'部门缩写', required=True)
