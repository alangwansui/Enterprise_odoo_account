# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Wizard_reject(models.TransientModel):
    _name = 'dtdream.customer.reception.wizard'

    liyou = fields.Text("理由", required=True)

    @api.multi
    def _message_poss(self, state, action, customer, reason=''):
        customer.message_post(body=u"""<table border="1" style="border-collapse: collapse;">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">理由</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, reason))

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        customer_reception = self.env['dtdream.customer.reception'].browse(self._context['active_id'])
        state = {'1': u'部门审批', '2': u'客工部审批'}
        self._message_poss(state=u'%s-->草稿' % state.get(customer_reception.state), action=u'驳回',
                           customer=customer_reception, reason='%s' % self.liyou)
        customer_reception.signal_workflow('btn_reject')


class Wizard_back(models.TransientModel):
    _name = 'dtdream.customer.reception.back.wizard'

    liyou = fields.Text("理由", required=True)

    @api.multi
    def _message_poss(self, state, action, customer, reason=''):
        customer.message_post(body=u"""<table border="1" style="border-collapse: collapse;">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">理由</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, reason))

    @api.one
    def btn_confirm(self):
        customer_reception = self.env['dtdream.customer.reception'].browse(self._context['active_id'])
        state = {'1': u'部门审批', '2': u'客工部审批', '3': u'接待安排与执行'}
        self._message_poss(state=u'%s-->草稿' % state.get(customer_reception.state), action=u'撤回',
                           customer=customer_reception, reason='%s' % self.liyou)
        customer_reception.signal_workflow('btn_back')

