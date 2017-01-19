# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv


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

    @api.multi
    def unlink(self):
        assets_place = []
        for rec in self:
            manage = self.env['dtdream.assets.management'].search([('store_place', '=', rec.id)])
            check = self.env['dtdream.assets.check'].search([('store_place', '=', rec.id)])
            if manage or check:
                assets_place.append(rec.name)
        if assets_place:
            raise osv.except_osv(u'资产存放地(%s)已被引用,无法删除!' % ','.join(assets_place))
        return super(dtdream_assets_store_place, self).unlink()

    name = fields.Char(string='名称', size=32)
    room_code = fields.Char(string='房间编号', size=16)
    room_info = fields.Char(string='房间说明', size=64)
    is_active = fields.Boolean(string='是否有效')

