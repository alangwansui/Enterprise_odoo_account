# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_assets_management_wizard(models.TransientModel):
    _name = 'dtdream.assets.management.wizard'

    has_label = fields.Selection([('0', '否'), ('1', '是')], string='标签是否粘贴')
    useable = fields.Selection([('0', '否'), ('1', '是')], string='是否可使用')
    unused = fields.Selection([('0', '否'), ('1', '是')], string='是否闲置')
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
        assets.write({"has_label": self.has_label, "useable": self.useable, "unused": self.unused, "mark": self.mark})
        self._message_poss(app=assets, state=u'未盘点-->已盘点', action=u'自盘', approve='')
        assets.signal_workflow('assets_submit')
