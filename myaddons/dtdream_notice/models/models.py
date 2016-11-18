# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions

class dtdream_notice(models.Model):
    _name = 'dtdream_notice.dtdream_notice'

    name = fields.Char(string=u'单据号')
    content = fields.Text(string=u'内容', required=True)
    url = fields.Char(string=u'地址', required=True)
    valid = fields.Boolean(string=u'有效', defualt=True)

    @api.model
    def create(self, vals):
        # 计算单号
        if ('name' not in vals) or (vals.get('name') in ('/', False)):
            vals['name'] = self.env['ir.sequence'].next_by_code('dtdream_notice.dtdream_notice')

        if ('url' in vals) and ((vals.get('url') in ('', False)) or (vals['url'].strip() == '') ):
            vals['url'] = "javascript:void(0)"

        result = super(dtdream_notice, self).create(vals)

        return result

    @api.multi
    def write(self, vals):
        if not self:
            return True
        if ('url' in vals) and ((vals.get('url') in ('', False)) or (vals['url'].strip() == '') ):
            vals['url'] = "javascript:void(0)"

        return super(dtdream_notice, self).write(vals)