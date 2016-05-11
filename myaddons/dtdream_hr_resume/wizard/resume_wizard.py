# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime


class CHWizard(models.TransientModel):
    _name = 'dtdream.resume.wizard'

    liyou = fields.Text("理由", required=True)

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        current_chucha = self.env['dtdream.hr.resume'].browse(self._context['active_id'])
        current_chucha.message_post(body=u"驳回," + u"理由:" + self.liyou)
        current_chucha.signal_workflow('btn_reject')
