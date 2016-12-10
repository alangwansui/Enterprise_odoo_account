# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_assets_store_place(models.Model):
    _name = 'dtdream.assets.store.place'

    name = fields.Char(string='名称', size=32)
    is_active = fields.Boolean(string='是否有效')

