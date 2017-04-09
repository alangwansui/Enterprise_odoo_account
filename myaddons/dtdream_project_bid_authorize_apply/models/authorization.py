# -*- coding: utf-8 -*-
from openerp import models, fields, api
class authorization(models.Model):
    _name = "dtdream.authorization"

    authorization_id = fields.Many2one("dtdream.project.bid.authorize.apply")
    content = fields.Char(string='内容')
