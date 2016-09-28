# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Wizard_reject(models.TransientModel):
    _name = 'dtdream.hr.performance.reject.wizard'

    liyou = fields.Text("理由", required=True)

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        performance = self.env['dtdream.hr.performance'].browse(self._context['active_id'])
        performance.message_post(body=u"返回修改," + u"理由:" + self.liyou)
        performance.signal_workflow('btn_revise')


class Wizard_agree(models.TransientModel):
    _name = 'dtdream.hr.performance.agree.wizard'

    liyou = fields.Text("意见")

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        performance = self.env['dtdream.hr.performance'].browse(self._context['active_id'])
        if self.liyou:
            body = u"同意," + u"建议:" + self.liyou
        else:
            body = u"同意"
        performance.message_post(body=body)
        performance.signal_workflow('btn_agree')

