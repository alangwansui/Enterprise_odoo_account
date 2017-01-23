# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv


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

    def need_column_date_header(self, cr, uid, context=None):
        return {}

    def return_vals_action(self, cr, uid, ids, this_id, context=None):
        return {'type': 'ir.actions.act_window',
                'res_model': 'dtimport.hr.performance',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': this_id,
                'views': [(False, 'form')],
                'target': 'new'}

    def judge_and_write_vals(self, cr, uid, ids, data_dict, context=None):
        pass




