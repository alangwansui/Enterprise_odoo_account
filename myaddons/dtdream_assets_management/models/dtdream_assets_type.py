# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv


class dtdream_assets_type(models.Model):
    _name = 'dtdream.assets.type'

    @api.multi
    def name_get(self):
        super(dtdream_assets_type, self).name_get()
        data = []
        for rec in self:
            code = ''
            code += rec.name + '-' + (rec.code or "")
            data.append((rec.id, code))
        return data

    @api.multi
    def unlink(self):
        assets_type = []
        for rec in self:
            manage = self.env['dtdream.assets.management'].search([('asset_type', '=', rec.id)])
            check = self.env['dtdream.assets.check'].search([('asset_type', '=', rec.id)])
            if manage or check:
                assets_type.append(rec.code)
        if assets_type:
            raise osv.except_osv(u'资产类别编码(%s)已被引用,无法删除!' % ','.join(assets_type))
        return super(dtdream_assets_type, self).unlink()

    name = fields.Char(string='资产类别名称', size=32)
    discount = fields.Integer(string='折旧年限(年)')
    code = fields.Char(string='资产类别编码', size=32)
    des = fields.Text(string='资产类别描述')
    account = fields.Char(string='会计科目名称', size=32)
    account_code = fields.Char(string='会计科目编码', size=16)
    account_level = fields.Integer(string='会计科目级次')
    disprice = fields.Float(string='资产残值')

    _sql_constraints = [
        ('asset_type_code_unique', 'UNIQUE(code)', "资产类别编码已存在!"),
    ]



