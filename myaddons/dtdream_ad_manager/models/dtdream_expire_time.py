# -*- coding: utf-8 -*-
from openerp import models, fields


# 域用户信息
class dtdream_expire_time(models.Model):
    _name = 'dtdream.expire.time'
    _description = u'域群组有效时长'

    name = fields.Char(string='有效时长')