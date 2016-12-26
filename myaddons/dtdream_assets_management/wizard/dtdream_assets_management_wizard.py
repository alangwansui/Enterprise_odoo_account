# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_assets_management_wizard(models.TransientModel):
    _name = 'dtdream.assets.management.wizard'

    @api.model
    def default_get(self, fields):
        rec = super(dtdream_assets_management_wizard, self).default_get(fields)
        check = self.env['dtdream.assets.check'].browse(self._context['active_id'])
        rec.update({"has_label": check.has_label, "useable": check.useable, "unused": check.unused,
                    "store_place": check.store_place.id})
        return rec

    has_label = fields.Selection([('0', '否'), ('1', '是')], string='标签是否粘贴')
    useable = fields.Selection([('0', '否'), ('1', '是')], string='是否可使用', default='1')
    unused = fields.Selection([('0', '否'), ('1', '是')], string='是否闲置', default='0')
    store_place = fields.Many2one('dtdream.assets.store.place', string='资产位置')
    selfcheck_date = fields.Date(string='自盘时间', default=lambda self: fields.Date.today())
    mark = fields.Text(string='备注')

    @api.multi
    def _message_poss(self, app, state, action, approve=''):
        app.message_post(body=u"""<table border="1" style="border-collapse: collapse;">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">下一处理人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, approve))

    @api.one
    def assets_submit(self):
        assets = self.env['dtdream.assets.check'].browse(self._context['active_id'])
        assets.write({"has_label": self.has_label, "useable": self.useable, "unused": self.unused, "mark": self.mark,
                      "store_place": self.store_place.id, "selfcheck_date": self.selfcheck_date})
        assets.assets_manage.write({"has_label": self.has_label, "useable": self.useable, "unused": self.unused,
                                    "mark": self.mark, "store_place": self.store_place.id,
                                    "selfcheck_date": self.selfcheck_date})
        self._message_poss(app=assets, state=u'未盘点-->已盘点', action=u'自盘', approve='')
        assets.signal_workflow('assets_submit')
