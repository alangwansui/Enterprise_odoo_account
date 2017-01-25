# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import re


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


class dtimport_hr_performance(osv.osv):
    _name = 'dtimport.hr.performance'
    _inherit = ['dtimport.wizard']

    def need_column_date_header(self):
        return {'workid': u'工号', 'quarter': u'考核季度', 'officer': u'一考主管', 'officer_sec': u'二考主管', 'result': u'考核结果'}

    def return_vals_action(self):
        return {'type': 'ir.actions.act_window',
                'res_model': 'dtimport.hr.performance',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new'}

    def judge_data_is_pass(self, record, need_head, header):
        for key, val in need_head.items():
            text = record[header.index(val)]
            if key in ['workid', 'officer', 'officer_sec'] and not text.isdigit():
                return {'code': 1000, 'message': u'%s格式错误' % val}
            elif key == 'quarter'and not re.match(u'(^\d{4}财年Q[1-4]$)|(^\d{4}财年年度$)', text):
                return {'code': 1001, 'message': u'考核季度的格式必须是XXXX财年Q1~Q4，' +
                                                 u'或XXXX财年年度；如2016财年Q1，或2016财年年度'}
        return {'code': 0, 'message': 'ok'}

    def judge_and_write_vals(self, data_dict):
        pass




