# -*- coding: utf-8 -*-
from openerp import models, fields, api

# 审批记录
class yunwei_config(models.Model):
    _name = "yunwei.config"

    name = fields.Char("运维参数配置",default="运维参数配置")
    list_price_coefficient = fields.Float(string="目录价系数(%)",required=True,default="6.75")
    cost_price_coefficient = fields.Float(string="成本系数(%)",required=True,default="20")