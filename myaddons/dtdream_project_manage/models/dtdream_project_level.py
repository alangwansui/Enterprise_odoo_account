# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_level(models.Model):
    _name = 'dtdream.project.level'

    name = fields.Char(string='等级名称', size=8)


class dtdream_project_type(models.Model):
    _name = 'dtdream.project.type'

    name = fields.Char(string='项目类型', size=16)