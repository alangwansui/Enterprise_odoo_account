# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv


class dtdream_assets_name(models.Model):
    _name = 'dtdream.assets.name'

    @api.multi
    def unlink(self):
        assets_name = []
        for rec in self:
            manage = self.env['dtdream.assets.management'].search([('asset_name', '=', rec.id)])
            check = self.env['dtdream.assets.check'].search([('asset_name', '=', rec.id)])
            if manage or check:
                assets_name.append(rec.name)
        if assets_name:
            raise osv.except_osv(u'资产名称(%s)已被引用,无法删除!' % ','.join(assets_name))
        return super(dtdream_assets_name, self).unlink()

    name = fields.Char(string='资产名称', size=32)

