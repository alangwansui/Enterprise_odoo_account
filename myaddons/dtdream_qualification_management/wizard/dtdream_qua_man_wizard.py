# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError, AccessError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
class dtdream_qua_man_wizard(models.TransientModel):
    _name = 'dtdream.qua.man.wizard'
    dead_line = fields.Datetime("截止时间")

    @api.multi
    def btn_confirm(self):
        import time
        t_in = time.clock()
        if self.dead_line:
            if self.dead_line <= datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
                raise ValidationError(u'截止时间应大于今天')
            context = dict(self._context or {})
            ids = context.get('active_ids', []) or []
            qualifications = self.env['dtdream.qualification.management'].browse(ids)
            for qua in qualifications:
                if qua.state == 'state1':
                    qua.state='state2'
                    qua.dead_line=self.dead_line
            logger.info( "========================btn_confirm=====================", time.clock() - t_in)
            return {'type': 'ir.actions.act_window_close'}
        else:
            raise ValidationError(u"请填写截止时间")


    @api.multi
    def btn_finish(self):
        context = dict(self._context or {})
        ids = context.get('active_ids', []) or []
        qualifications = self.env['dtdream.qualification.management'].browse(ids)
        for qua in qualifications:
            if not qua.result_post or not qua.result_rank:
                raise ValidationError(u'批次'+qua.batchnumber+u'的'+qua.name.name+ u"员工考核结果未录入，请录入!")
            else:
                if qua.state == 'state2':
                    qua.state = 'state3'
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def btn_email(self):
        import time
        t_in = time.clock()
        context = dict(self._context or {})
        ids = context.get('active_ids', []) or []
        number = 10
        config_list = self.env["dtdream.email.number"].sudo().search([])
        if len(config_list)>0:
            number = config_list[0].number
        if len(ids)<=int(number):
            qualifications = self.env['dtdream.qualification.management'].browse(ids)
            for qua in qualifications:
                qua.send_youcui_email()
                qua.is_today_youcui = True
        else:
            raise ValidationError(u"一次提醒不多于"+str(number)+u"条")
        logger.info("========================btn_email=====================", time.clock() - t_in)