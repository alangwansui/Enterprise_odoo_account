# -*- coding: utf-8 -*-

from openerp import models, fields, api
class dtdream_security_list_other(models.Model):
    _name = "dtdream.security.list.other"
    _description = "权限申请列表"

    security_other= fields.Many2one("dtdream.information.purview")

    space = fields.Char(string="空间")
    description = fields.Char(string="描述")
    read_right = fields.Boolean(string="读权限")
    write_right = fields.Boolean(string="写权限")