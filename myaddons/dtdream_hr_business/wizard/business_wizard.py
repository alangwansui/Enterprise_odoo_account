# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class businessWizard(models.TransientModel):
    _name = 'dtdream_hr_business.dtdream_hr_business.wizard'
    reason = fields.Text("驳回，驳回原因：",required="1")


    @api.one
    def btn_confirm(self):
    	# 将理由发送到chatter
        current_business = self.env['dtdream_hr_business.dtdream_hr_business'].browse(self._context['active_id'])
        current_business.message_post(body=u'驳回原因：'+self.reason)
        current_business.signal_workflow('wizard_refuse')