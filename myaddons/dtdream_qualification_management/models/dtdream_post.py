# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_post(models.Model):
    _name = 'dtdream.post'

    name = fields.Char(string="岗位名称",required=True)
    code = fields.Char(string="岗位编号",required=True)
    description = fields.Char(string="岗位明细")
    post_type_id = fields.Many2one('dtdream.post.type',string="职位族",required=True)