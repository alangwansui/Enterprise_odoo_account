# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError

#u中止导向

class dtdream_termination_wizard(models.TransientModel):
    _name = "dtdream.termination.wizard"

    reason=fields.Text(string="原因")

    @api.multi
    def _message_poss(self,suspension,current_approver,statechange,result,reason,):
        reason = reason or u'无'
        current_approver = current_approver.name or u'无'
        suspension.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">描述</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">审批人</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">审批结果</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">审批意见</td><td style="padding:10px">%s</td></tr>
                                               </table>""" %(suspension.name,statechange,current_approver,result,reason))

    @api.multi
    def btn_agree(self):
        active_id = self._context['active_id']
        current_termination = self.env['dtdream.prod.termination'].browse(active_id)
        current_termination.write({'current_approver_user': False,'state':'ysp'})
        self._message_poss(suspension=current_termination,statechange=u'审批中->已审批',current_approver=current_termination.current_approver,reason=self.reason,
                           result=u'同意')
        project = current_termination.project
        if not current_termination.version:
            if project.state=='state_01':
                project.state_old='state_01'
                project.signal_workflow('lixiang_to_zhongzhi')
            if project.state=='state_02':
                project.state_old='state_02'
                project.signal_workflow('ztsj_to_zhongzhi')
            if project.state=='state_03':
                project.state_old='state_03'
                project.signal_workflow('ddkf_to_zhongzhi')
            if project.state=='state_04':
                project.state_old='state_04'
                project.signal_workflow('yzfb_to_zhongzhi')
            if project.state=='state_06':
                project.state_old='state_06'
                self.signal_workflow('zanting_to_zhongzhi')
        else:
            version = current_termination.version
            if version.version_state=='initialization':
                version.version_state_old='initialization'
                version.signal_workflow('draft_to_vzhongzhi')
            if version.version_state=='Development':
                version.version_state_old='Development'
                version.signal_workflow('kaifa_to_vzhongzhi')
            if version.version_state=='pending':
                version.version_state_old='pending'
                version.signal_workflow('dfb_to_vzhongzhi')
            if version.version_state=='pause':
                version.version_state_old='pause'
                version.signal_workflow('vzanting_to_vzhongzhi')
        if not current_termination.version:
            current_termination.project.write({'is_zhongzhitjN':False})
        else:
            current_termination.version.write({'is_zhongzhitjN':False})

    @api.multi
    def btn_disagree(self):
        if not self.reason:
            raise ValidationError(u'原因不能为空')
        active_id = self._context['active_id']
        current_termination = self.env['dtdream.prod.termination'].browse(active_id)
        current_termination.write({'current_approver_user': False,'state':'ysp'})
        self._message_poss(suspension=current_termination,statechange=u'审批中->已审批',current_approver=current_termination.current_approver,reason=self.reason,
                           result=u'不同意')
        if not current_termination.version:
            current_termination.project.write({'is_zhongzhitjN':False})
        else:
            current_termination.version.write({'is_zhongzhitjN':False})
