# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_pmo_approve_wizard(models.TransientModel):
    _name = 'dtdream.pmo.approve.wizard'

    reason = fields.Text(string="理由", required=True, size=30)

    @api.multi
    def record_action_message(self, project, state, action, reason=''):
        project.message_post(body=u"""<table border="1" style="border-collapse: collapse;table-layout: fixed">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px;">原因</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, reason))

    @api.one
    def btn_confirm(self):
        model_name = self._context.get('active_model')
        if model_name in['dtdream.project.output.plan.manage', 'dtdream.project.output.deliver.manage']:
            record = self.env[model_name].browse(self._context['active_id'])
            record.write({'assess_time': fields.date.today(), 'state': '3', 'assess_times': record.assess_times + 1})
            record.update_current_approve()
        else:
            project = self.env['dtdream.project.manage'].browse(self._context['active_id'])
            if project.state_y == '12':
                approve_list = project.get_approve_list(result=True, suggestion=u'不同意, %s' % self.reason)
                project.write({'current_approve': [(6, 0, approve_list)]})
                self.record_action_message(project, state=u'交付服务经理确认', action=u'不同意', reason=self.reason)
            elif project.state_y == '21':
                project.signal_workflow('approve_reject')
