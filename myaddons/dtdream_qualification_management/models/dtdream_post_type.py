# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_post_type(models.Model):
    _name = 'dtdream.post.type'

    name = fields.Char(string="职位族",required=True)
    post_ids = fields.One2many('dtdream.post','post_type_id',string="岗位")
