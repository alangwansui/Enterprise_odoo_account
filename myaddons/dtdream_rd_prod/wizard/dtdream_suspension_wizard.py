# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError

#暂停导向

class dtdream_suspension_wizard(models.TransientModel):
    _name = "dtdream.suspension.wizard"

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
        current_suspension = self.env['dtdream.prod.suspension'].browse(active_id)
        current_suspension.write({'current_approver_user': False,'state':'ysp'})
        self._message_poss(suspension=current_suspension,statechange=u'审批中->已审批',current_approver=current_suspension.current_approver,reason=self.reason,
                           result=u'同意')
        project = current_suspension.project
        if not current_suspension.version:
            if project.state=='state_01':
                project.state_old='state_01'
                project.signal_workflow('lixiang_to_zanting')
            if project.state=='state_02':
                project.state_old='state_02'
                project.signal_workflow('ztsj_to_zanting')
            if project.state=='state_03':
                project.state_old='state_03'
                project.signal_workflow('ddkf_to_zanting')
            if project.state=='state_04':
                project.state_old='state_04'
                project.signal_workflow('yzfb_to_zanting')
        else:
            version = current_suspension.version
            if version.version_state=='initialization':
                version.version_state_old='initialization'
                version.signal_workflow('draft_to_vzanting')
            if version.version_state=='Development':
                version.version_state_old='Development'
                version.signal_workflow('kaifa_to_vzanting')
            if version.version_state=='pending':
                version.version_state_old='pending'
                version.signal_workflow('dfb_to_vzanting')
        if not current_suspension.version:
            current_suspension.project.write({'is_zantingtjN':False})
        else:
            current_suspension.version.write({'is_zantingtjN':False})


    @api.multi
    def btn_disagree(self):
        if not self.reason:
            raise ValidationError(u'原因不能为空')
        active_id = self._context['active_id']
        current_suspension = self.env['dtdream.prod.suspension'].browse(active_id)
        current_suspension.write({'current_approver_user': False,'state':'ysp'})
        self._message_poss(suspension=current_suspension,statechange=u'审批中->已审批',current_approver=current_suspension.current_approver,reason=self.reason,
                           result=u'不同意')
        if not current_suspension.version:
            current_suspension.project.write({'is_zantingtjN':False})
        else:
            current_suspension.version.write({'is_zantingtjN':False})
