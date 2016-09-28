# -*- coding: utf-8 -*-

from openerp import models, fields, api


class CHWizardMODIFY(models.TransientModel):
    _name = 'dtdream.resume.modify.wizard'

    liyou = fields.Text("理由", required=True)

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        current_modify = self.env['dtdream.hr.resume.modify'].browse(self._context['active_id'])
        current_modify.message_post(body=u"驳回," + u"理由:" + self.liyou)
        current_modify.signal_workflow('btn_reject')
