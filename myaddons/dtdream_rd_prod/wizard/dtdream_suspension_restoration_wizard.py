# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError

#恢复暂停导向

class dtdream_suspension_restoration_wizard(models.TransientModel):
    _name = "dtdream.suspension.restoration.wizard"

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
        current_suspension = self.env['dtdream.prod.suspension.restoration'].browse(active_id)
        current_suspension.write({'current_approver_user': False,'state':'ysp'})
        self._message_poss(suspension=current_suspension,statechange=u'审批中->已审批',current_approver=current_suspension.current_approver,reason=self.reason,
                           result=u'同意')
        project = current_suspension.project
        if not current_suspension.version:
            if project.state_old=='state_01':
                project.signal_workflow('zanting_to_lixiang')
            if project.state_old=='state_02':
                project.signal_workflow('zanting_to_ztsj')
            if project.state_old=='state_03':
                project.signal_workflow('zanting_to_ddkf')
            if project.state_old=='state_04':
                project.signal_workflow('zanting_to_yzfb')
        else:
            version = current_suspension.version
            if version.version_state_old=='initialization':
                version.signal_workflow('vzanting_to_draft')
            if version.version_state_old=='Development':
                version.signal_workflow('vzanting_to_kaifa')
            if version.version_state_old=='pending':
                version.signal_workflow('vzanting_to_dfb')
        if not current_suspension.version:
            current_suspension.project.write({'is_zanting_backtjN':False})
        else:
            current_suspension.version.write({'is_zanting_backtjN':False})

    @api.multi
    def btn_disagree(self):
        if not self.reason:
            raise ValidationError(u'原因不能为空')
        active_id = self._context['active_id']
        current_suspension = self.env['dtdream.prod.suspension.restoration'].browse(active_id)
        current_suspension.write({'current_approver_user': False,'state':'ysp'})
        self._message_poss(suspension=current_suspension,statechange=u'审批中->已审批',current_approver=current_suspension.current_approver,reason=self.reason,
                           result=u'不同意')
        if not current_suspension.version:
            current_suspension.project.write({'is_zanting_backtjN':False})
        else:
            current_suspension.version.write({'is_zanting_backtjN':False})