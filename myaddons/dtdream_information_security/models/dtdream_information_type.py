# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class dtdream_information_type(models.Model):
    _name = "dtdream.information.type"
    name= fields.Char(string="名称")
    desc = fields.Text(string="描述")
    url = fields.Char(string="地址链接")
    user = fields.Char(string="登录帐号")
    passw =fields.Char(string="登录密码")
    admin = fields.Many2one("hr.employee",string="管理员")
    type = fields.Selection([('confluence','confluence'),('git','git'),('other','其他')],string="类别")