# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime


class dtdream_reserve_wizard(models.TransientModel):
    _name = 'dtdream.reserve.wizard'

    def get_selection(self):
        selection_list = []
        if 'active_id' in self._context:
            current_record = self.env['dtdream.reserve.fund'].browse(self._context['active_id'])
            state_list = current_record.his_state.split(',')
            state_list.remove(current_record.state)
            for rec in state_list:
                selection_list.append((rec, rec))
        return selection_list

    reason = fields.Char(string='意见')
    result = fields.Char(string='结果')
    state = fields.Selection(string='驳回节点', selection=get_selection)

    @api.one
    def btn_confirm(self):
        current_record = self.env['dtdream.reserve.fund'].browse(self._context['active_id'])
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        state_old = current_record.state
        result_chinese = ''
        current_record.write({"his_handler": [(4, current_employee.id)]})
        people_email_list = ''
        for person in current_record.current_handler:
            if self.env.user.id != person.user_id.id:
                people_email_list += person.work_email+';'
        if people_email_list:
            self.env['mail.mail'].create({
                'subject': u'【dodo提醒】%s提交的单号为：%s 的备用金申请已被处理！'
                           % (current_record.applicant.name, current_record.name),
                'body_html': u'''
                <p>您好，</p>
                <p>%s提交的备用金申请已被他人处理，您无需再处理！</p>
                <p>dodo</p>
                <p>万千业务，简单有do</p>
                <p>%s</p>
                ''' % (current_record.applicant.name, datetime.today().strftime('%Y-%m-%d')),
                'email_from': self.env['ir.mail_server'].search([], limit=1).smtp_user,
                'email_to': people_email_list,
            }).send()
        if self.result == 'agree':
            current_record.signal_workflow('btn_agree')
            result_chinese = u'同意'
        elif self.result == 'reject':
            if self.state == u'草稿':
                current_record.reject_state = 'draft'
            elif self.state == u'主管审批':
                current_record.reject_state = 'manager'
            elif self.state == u'第一权签人审批':
                current_record.reject_state = 'first'
            elif self.state == u'第二权签人审批':
                current_record.reject_state = 'second'
            elif self.state == u'总裁审批':
                current_record.reject_state = 'president'
            elif self.state == u'接口会计审批':
                current_record.reject_state = 'interface'
            result_chinese = u'驳回'
            current_record.signal_workflow('btn_reject')
        state_new = current_record.state
        current_record.message_post(body=u"审批结果：%s，审批意见：%s，状态：%s --> %s"
                                         % (result_chinese, self.reason or "", state_old, state_new))


