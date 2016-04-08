# -*- coding: utf-8 -*-

from openerp import models, fields, api


class CHWizard(models.TransientModel):
    _name = 'dtdream.travel.wizard'

    liyou = fields.Text("理由", required=True)

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        current_chucha = self.env['dtdream.travel.chucha'].browse(self._context['active_id'])
        current_chucha.message_post(body=self.liyou)
        current_chucha.signal_workflow('btn_reject')
