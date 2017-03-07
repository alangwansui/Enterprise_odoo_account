# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class dtdream_information_type(models.Model):
    _name = "dtdream.information.type"
    name= fields.Char(string="名称",required=True)
    desc = fields.Text(string="描述")
    url = fields.Char(string="地址链接",required=True)
    user = fields.Char(string="登录帐号")
    passw =fields.Char(string="登录密码")
    admin = fields.Many2one("hr.employee",string="管理员",required=True)
    token = fields.Char(string="token")
    git_group = fields.Char(string="git群组")
    type = fields.Selection([('confluence','Confluence'),('git','Gitlab')],string="类别",default='confluence',required=True)
    is_conf = fields.Boolean(string="标记是否是confluence",default=True)
    is_git = fields.Boolean(string="标记是否是git",default=False)

    @api.constrains("type")
    def _constraint_type(self):
        if self.type=='confluence':
            if not self.user or not self.passw:
                raise ValidationError(u'登录帐号和登录密码必填')
        else:
            if not self.token or not self.git_group:
                raise ValidationError(u'token和群组必填')

    @api.onchange("type")
    def _onchange_type(self):
        if self.type=='confluence':
            self.is_conf=True
            self.is_git=False
        else:
            self.is_conf=False
            self.is_git=True