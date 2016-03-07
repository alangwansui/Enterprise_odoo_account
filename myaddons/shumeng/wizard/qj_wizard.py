# -*- coding: utf-8 -*-

from openerp import models, fields, api

class QjWizard(models.TransientModel):
    _name = 'shumeng.qingjia.wizard'


    liyou = fields.Text("理由", required=True)

    @api.one
    def btn_confirm(self):
    	# 将理由发送到chatter
        current_qingjiadan = self.env['shumeng.qingjiadan'].browse(self._context['active_id'])
        current_qingjiadan.message_post(body=self.liyou)
        current_qingjiadan.signal_workflow('wizard_refuse')