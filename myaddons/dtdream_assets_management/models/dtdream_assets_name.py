# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_assets_name(models.Model):
    _name = 'dtdream.assets.name'

    name = fields.Char(string='资产名称', size=32)

