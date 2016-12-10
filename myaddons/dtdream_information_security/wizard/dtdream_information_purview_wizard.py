# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
class dtdream_information_purview_wizard(models.TransientModel):
    _name = "dtdream.information.purview.wizard"
    name= fields.Char()
    reason = fields.Text(string="原因")


    @api.multi
    def _message_poss(self,approval,current_approver,statechange,result,reason,next_shenpiren=None):
        reason = reason or u'无'
        next_shenpiren = next_shenpiren or u'无'
        approval.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">清单</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">审批人</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">审批结果</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">审批意见</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">下阶段处理人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" %(approval.name,statechange,current_approver.name,result,reason,next_shenpiren))

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    @api.multi
    def _send_email(self,approval,next_approver):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.information.purview' % approval.id
        url = base_url+link
        appellation = next_approver.name+u",您好"
        subject=approval.applicant.name+u"提交的权限申请，等待您的审批"
        content = approval.applicant.name+u"提交的‘"+approval.name+u"’的权限申请进入‘所有人审批’阶段，等待您的审批"
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

    #同意
    @api.multi
    def btn_agree(self):
        approval = self.env['dtdream.information.purview'].browse(self._context['active_id'])
        approval.write({'his_approver_user': [(4, approval.current_approver_user.id)]})
        if approval.state=="state_02":
            if approval.manager==approval.information_syr:
                approval.signal_workflow('zgsp_to_wc')
                self._message_poss(approval=approval,current_approver=approval.current_approver,statechange=u'主管审批->完成',result=u'同意',reason=self.reason)
                approval.current_approver_user=False
            else:
                approval.signal_workflow('zgsp_to_syrsp')
                self._message_poss(approval=approval,current_approver=approval.current_approver,statechange=u'主管审批->所有人审批',result=u'同意',reason=self.reason,next_shenpiren=approval.information_syr.name)
                approval.write({'current_approver_user': approval.information_syr.user_id.id})
                self._send_email(approval=approval,next_approver=approval.information_syr)
        elif approval.state=="state_03":
            approval.signal_workflow('syrsp_to_wc')
            self._message_poss(approval=approval,current_approver=approval.current_approver,statechange=u'所有人审批->完成',result=u'同意',reason=self.reason)
            approval.current_approver_user=False
            approval.permission_settings()

    #驳回
    @api.multi
    def btn_overrule(self):
        approval = self.env['dtdream.information.purview'].browse(self._context['active_id'])
        approval.write({'his_approver_user': [(4, approval.current_approver_user.id)]})
        if approval.state=="state_02":
            approval.signal_workflow('zgsp_to_cg')
            self._message_poss(approval=approval,current_approver=approval.current_approver,statechange=u'主管审批->草稿',result=u'驳回',reason=self.reason)
            approval.current_approver_user=False
        elif approval.state=="state_03":
            approval.signal_workflow('syrsp_to_cg')
            self._message_poss(approval=approval,current_approver=approval.current_approver,statechange=u'所有人审批->草稿',result=u'驳回',reason=self.reason)
            approval.current_approver_user=False

    #不同意
    @api.multi
    def btn_disagree(self):
        approval = self.env['dtdream.information.purview'].browse(self._context['active_id'])
        approval.write({'his_approver_user': [(4, approval.current_approver_user.id)]})
        if approval.state=="state_02":
            approval.signal_workflow('zgsp_to_zhongzhi')
            self._message_poss(approval=approval,current_approver=approval.current_approver,statechange=u'主管审批->终止',result=u'不同意',reason=self.reason)
            approval.current_approver_user=False
        elif approval.state=="state_03":
            approval.signal_workflow('syrsp_to_zhongzhi')
            self._message_poss(approval=approval,current_approver=approval.current_approver,statechange=u'所有人审批->终止',result=u'不同意',reason=self.reason)
            approval.current_approver_user=False