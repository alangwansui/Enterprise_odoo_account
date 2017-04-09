# -*- coding: utf-8 -*-
from openerp import models, fields


# 域用户信息
class dtdream_ad_ext(models.Model):
    _name = 'dtdream.ad.ext'
    _description = u'扩展信息'

    name = fields.Char(string=u'扩展名称', required=True)
    value = fields.Char(string=u'扩展缩写', required=True)
