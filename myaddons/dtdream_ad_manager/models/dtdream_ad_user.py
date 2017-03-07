# -*- coding: utf-8 -*-
from openerp import models, fields


# 域用户信息
class dtdream_ad_user(models.Model):
    _name = 'dtdream.ad.user'
    _description = u'域用户信息'

    user_name = fields.Char(string=u'用户名称')
    active = fields.Boolean(string=u'是否有效用户')
    display_name = fields.Char(string=u'显示名称')
    email = fields.Char(string=u'邮箱')
    phone = fields.Char(string=u'手机')
    expire_time = fields.Datetime(string=u'超期时间')
