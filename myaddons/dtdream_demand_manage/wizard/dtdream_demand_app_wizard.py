# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Wizard_reject(models.TransientModel):
    _name = 'dtdream.demand.app.wizard'

    liyou = fields.Text("理由")

    @api.multi
    def _message_poss(self, state, action, app, reason=''):
        app.message_post(body=u"""<table border="1" style="border-collapse: collapse;">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">理由</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, reason))

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        demand_app = self.env['dtdream.demand.app'].browse(self._context['active_id'])
        state = {'1': u'部门主管审批', '2': u'IT需求审批', '4': u'IT方案审批'}
        self._message_poss(state=u'%s-->草稿' % state.get(demand_app.state) if demand_app.state != '4' else u'IT方案审批-->IT方案分析', action=u'驳回', app=demand_app, reason='%s' % self.liyou)
        demand_app.signal_workflow('btn_reject')
