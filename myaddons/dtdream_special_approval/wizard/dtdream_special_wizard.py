# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
class dtdream_special_wizard(models.Model):
    _name = "dtdream.special.wizard"
    name= fields.Char()
    reason = fields.Text(string="原因")


    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    def add_follower(self, cr, uid, ids, employee_id, context=None):
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        if employee and employee.user_id:
            self.message_subscribe_users(cr, uid, ids, user_ids=[employee.user_id.id], context=context)

    @api.multi
    def _send_email(self,approval,next_approver):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.special.approval' % approval.id
        url = base_url+link
        appellation = next_approver.name+u",您好"
        subject=approval.applicant.name+u"提交的编号为‘"+approval.name+u"’的专项审批，等待您的审批"
        content = approval.applicant.name+u"提交的编号为‘"+approval.name+u"’的专项审批，等待您的审批"
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,approval.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % next_approver.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()
        # self.add_follower(employee_id=current_approver.id)

    @api.one
    def _message_poss(self,approval,current_approver,statechange,result,reason,next_shenpiren=None):
        reason = reason or u'无'
        next_shenpiren = next_shenpiren or u'无'
        approval.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">专项编号</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">审批人</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">审批结果</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">审批意见</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">下阶段审批人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" %(approval.name,statechange,current_approver.name,result,reason,next_shenpiren))

    @api.one
    def btn_agree(self):
        approval = self.env['dtdream.special.approval'].browse(self._context['active_id'])
        self.write({'deadline':datetime.now() + relativedelta(days=2)})
        approval.write({'his_approver_user': [(4, approval.current_approver_user.id)]})
        if approval.state=='state_02':
            if approval.help_state=='department_01':
                if approval.shenpi_zer_shouyi:
                    self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_zer_shouyi.name)
                    approval.write({'current_approver_user': approval.shenpi_zer_shouyi.user_id.id,'help_state':'department_02'})
                    self._send_email(approval=approval,next_approver=approval.shenpi_zer_shouyi)
                elif approval.shenpi_fir or approval.shenpi_sec or approval.shenpi_thr or approval.shenpi_fou:
                    approval.signal_workflow('zgsp_to_qqrsp')
                    if approval.shenpi_fir:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fir.name)
                        approval.write({'current_approver_user': approval.shenpi_fir.user_id.id,'help_state':'quanqian_01'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fir)
                    elif approval.shenpi_sec:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_sec.name)
                        approval.write({'current_approver_user': approval.shenpi_sec.user_id.id,'help_state':'quanqian_02'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_sec)
                    elif approval.shenpi_thr:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_thr.name)
                        approval.write({'current_approver_user': approval.shenpi_thr.user_id.id,'help_state':'quanqian_03'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_thr)
                    elif approval.shenpi_fou:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fou.name)
                        approval.write({'current_approver_user': approval.shenpi_fou.user_id.id,'help_state':'quanqian_04'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fou)
                elif approval.shenpi_fif or approval.shenpi_six:
                    approval.signal_workflow('zgsp_to_cwsp')
                    if approval.shenpi_fif:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fif.name)
                        approval.write({'current_approver_user': approval.shenpi_fif.user_id.id,'help_state':'cw_01'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fif)
                    elif approval.shenpi_six:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_six.name)
                        approval.write({'current_approver_user': approval.shenpi_six.user_id.id,'help_state':'cw_02'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_six)
            elif approval.help_state=='department_02':
                if approval.shenpi_fir or approval.shenpi_sec or approval.shenpi_thr or approval.shenpi_fou:
                    approval.signal_workflow('zgsp_to_qqrsp')
                    if approval.shenpi_fir:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fir.name)
                        approval.write({'current_approver_user': approval.shenpi_fir.user_id.id,'help_state':'quanqian_01'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fir)
                    elif approval.shenpi_sec:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_sec.name)
                        approval.write({'current_approver_user': approval.shenpi_sec.user_id.id,'help_state':'quanqian_02'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_sec)
                    elif approval.shenpi_thr:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_thr.name)
                        approval.write({'current_approver_user': approval.shenpi_thr.user_id.id,'help_state':'quanqian_03'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_thr)
                    elif approval.shenpi_fou:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fou.name)
                        approval.write({'current_approver_user': approval.shenpi_fou.user_id.id,'help_state':'quanqian_04'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fou)
                elif approval.shenpi_fif or approval.shenpi_six:
                    approval.signal_workflow('zgsp_to_cwsp')
                    if approval.shenpi_fif:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fif.name)
                        approval.write({'current_approver_user': approval.shenpi_fif.user_id.id,'help_state':'cw_01'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fif)
                    elif approval.shenpi_six:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_zer,statechange=u'主管审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_six.name)
                        approval.write({'current_approver_user': approval.shenpi_six.user_id.id,'help_state':'cw_02'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_six)
        elif approval.state=='state_03':
            if approval.help_state=='quanqian_01':
                if approval.shenpi_sec or approval.shenpi_thr or approval.shenpi_fou:
                    if approval.shenpi_sec:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_fir,statechange=u'权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_sec.name)
                        approval.write({'current_approver_user': approval.shenpi_sec.user_id.id,'help_state':'quanqian_02'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_sec)
                    elif approval.shenpi_thr:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_fir,statechange=u'权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_thr.name)
                        approval.write({'current_approver_user': approval.shenpi_thr.user_id.id,'help_state':'quanqian_03'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_thr)
                    elif approval.shenpi_fou:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_fir,statechange=u'权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fou.name)
                        approval.write({'current_approver_user': approval.shenpi_fou.user_id.id,'help_state':'quanqian_04'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fou)
                elif approval.shenpi_fif or approval.shenpi_six:
                    approval.signal_workflow('qqrsp_to_cwsp')
                    if approval.shenpi_fif:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_fir,statechange=u'权签人审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fif.name)
                        approval.write({'current_approver_user': approval.shenpi_fif.user_id.id,'help_state':'cw_01'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fif)
                    elif approval.shenpi_six:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_fir,statechange=u'权签人审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_six.name)
                        approval.write({'current_approver_user': approval.shenpi_six.user_id.id,'help_state':'cw_02'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_six)
            elif approval.help_state=='quanqian_02':
                if approval.shenpi_thr or approval.shenpi_fou:
                    if approval.shenpi_thr:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_sec,statechange=u'权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_thr.name)
                        approval.write({'current_approver_user': approval.shenpi_thr.user_id.id,'help_state':'quanqian_03'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_thr)
                    elif approval.shenpi_fou:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_sec,statechange=u'权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fou.name)
                        approval.write({'current_approver_user': approval.shenpi_fou.user_id.id,'help_state':'quanqian_04'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fou)
                elif approval.shenpi_fif or approval.shenpi_six:
                    approval.signal_workflow('qqrsp_to_cwsp')
                    if approval.shenpi_fif:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_sec,statechange=u'权签人审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fif.name)
                        approval.write({'current_approver_user': approval.shenpi_fif.user_id.id,'help_state':'cw_01'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fif)
                    elif approval.shenpi_six:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_sec,statechange=u'权签人审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_six.name)
                        approval.write({'current_approver_user': approval.shenpi_six.user_id.id,'help_state':'cw_02'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_six)
            elif approval.help_state=='quanqian_03':
                if approval.shenpi_fou:
                    if approval.shenpi_fou:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_sec,statechange=u'权签人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fou.name)
                        approval.write({'current_approver_user': approval.shenpi_fou.user_id.id,'help_state':'quanqian_04'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fou)
                elif approval.shenpi_fif or approval.shenpi_six:
                    approval.signal_workflow('qqrsp_to_cwsp')
                    if approval.shenpi_fif:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_sec,statechange=u'权签人审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fif.name)
                        approval.write({'current_approver_user': approval.shenpi_fif.user_id.id,'help_state':'cw_01'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_fif)
                    elif approval.shenpi_six:
                        self._message_poss(approval=approval,current_approver=approval.shenpi_sec,statechange=u'权签人审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_six.name)
                        approval.write({'current_approver_user': approval.shenpi_six.user_id.id,'help_state':'cw_02'})
                        self._send_email(approval=approval,next_approver=approval.shenpi_six)
            elif approval.help_state=='quanqian_04':
                approval.signal_workflow('qqrsp_to_cwsp')
                if approval.shenpi_fif:
                    self._message_poss(approval=approval,current_approver=approval.shenpi_sec,statechange=u'权签人审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_fif.name)
                    approval.write({'current_approver_user': approval.shenpi_fif.user_id.id,'help_state':'cw_01'})
                    self._send_email(approval=approval,next_approver=approval.shenpi_fif)
                elif approval.shenpi_six:
                    self._message_poss(approval=approval,current_approver=approval.shenpi_sec,statechange=u'权签人审批->财务审批',result=u'同意',reason=self.reason,next_shenpiren=approval.shenpi_six.name)
                    approval.write({'current_approver_user': approval.shenpi_six.user_id.id,'help_state':'cw_02'})
                    self._send_email(approval=approval,next_approver=approval.shenpi_six)
        elif approval.state=='state_04':
            if approval.help_state=='cw_01':
                if approval.shenpi_six:
                    self._message_poss(approval=approval,current_approver=approval.shenpi_fif,statechange=u'财务审批',result=u'同意',reason=self.reason,next_approver=approval.shenpi_six.name)
                    approval.write({'current_approver_user': approval.shenpi_six.user_id.id,'help_state':'cw_02'})
                    self._send_email(approval=approval,next_approver=approval.shenpi_six)
                else:
                    self._message_poss(approval=approval,current_approver=approval.shenpi_fif,statechange=u'财务审批->完成',result=u'同意',reason=self.reason)
                    approval.write({'current_approver_user': False})
                    approval.signal_workflow('cwsp_to_wc')
            elif approval.help_state=='cw_02':
                self._message_poss(approval=approval,current_approver=approval.shenpi_six,statechange=u'财务审批->完成',result=u'同意',reason=self.reason)
                approval.signal_workflow('cwsp_to_wc')
                approval.write({'current_approver_user': False})

    @api.one
    def btn_overrule(self):
        if not self.reason:
            raise ValidationError(u'驳回时请填写原因')
        approval = self.env['dtdream.special.approval'].browse(self._context['active_id'])
        em = self.env['hr.employee'].search([('user_id','=',approval.current_approver_user.id)])
        approval.write({'his_approver_user': [(4, approval.current_approver_user.id)]})
        if approval.state=='state_02':
            approval.signal_workflow('zgsp_to_cg')
            self._message_poss(approval=approval,current_approver=em,statechange=u'主管审批->草稿',result=u'驳回',reason=self.reason)
        if approval.state=='state_03':
            approval.signal_workflow('qqrsp_to_cg')
            self._message_poss(approval=approval,current_approver=em,statechange=u'权签人审批->草稿',result=u'驳回',reason=self.reason)
        if approval.state=='state_04':
            approval.signal_workflow('cwsp_to_cg')
            self._message_poss(approval=approval,current_approver=em,statechange=u'财务审批->草稿',result=u'驳回',reason=self.reason)
        approval.current_approver_user=False

    @api.one
    def _message_poss_selfback(self,approval,current_approver,statechange,action,reason):
        reason = reason or u'无'
        approval.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">专项编号</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作者</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">理由</td><td style="padding:10px">%s</td></tr>
                                               </table>""" %(approval.name,statechange,current_approver.name,action,reason))

    @api.one
    def btn_selfback(self):
        if not self.reason:
            raise ValidationError(u'撤回时请填写理由')
        approval = self.env['dtdream.special.approval'].browse(self._context['active_id'])
        em = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        if approval.state=='state_02':
            approval.signal_workflow('zgsp_to_cg')
            self._message_poss_selfback(approval=approval,current_approver=em,statechange=u'主管审批->草稿',action=u'撤回',reason=self.reason)
        if approval.state=='state_03':
            approval.signal_workflow('qqrsp_to_cg')
            self._message_poss_selfback(approval=approval,current_approver=em,statechange=u'权签人审批->草稿',action=u'撤回',reason=self.reason)
        if approval.state=='state_04':
            approval.signal_workflow('cwsp_to_cg')
            self._message_poss_selfback(approval=approval,current_approver=em,statechange=u'财务审批->草稿',action=u'撤回',reason=self.reason)
        approval.current_approver_user=False