# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_assets_supply(models.Model):
    _name = 'dtdream.assets.supply'

    name = fields.Char(string='供应商', size=32)

