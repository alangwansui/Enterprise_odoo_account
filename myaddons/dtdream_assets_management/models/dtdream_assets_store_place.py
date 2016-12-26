# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_assets_store_place(models.Model):
    _name = 'dtdream.assets.store.place'

    @api.multi
    def name_get(self):
        super(dtdream_assets_store_place, self).name_get()
        data = []
        for rec in self:
            place = ''
            place += rec.name + ('-' + rec.room_code if rec.room_code else "")
            data.append((rec.id, place))
        return data

    name = fields.Char(string='名称', size=32)
    room_code = fields.Char(string='房间编号', size=16)
    room_info = fields.Char(string='房间说明', size=64)
    is_active = fields.Boolean(string='是否有效')

