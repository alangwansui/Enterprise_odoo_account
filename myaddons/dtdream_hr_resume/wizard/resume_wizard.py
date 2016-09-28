# -*- coding: utf-8 -*-

from openerp import models, fields, api


class CHWizardRESUME(models.TransientModel):
    _name = 'dtdream.resume.wizard'

    liyou = fields.Text("理由", required=True)

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        current_resume = self.env['dtdream.hr.resume'].browse(self._context['active_id'])
        current_resume.message_post(body=u"驳回," + u"理由:" + self.liyou)
        current_resume.signal_workflow('btn_reject')
