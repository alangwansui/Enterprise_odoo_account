# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
class dtdream_information_shouquan_wizard(models.TransientModel):
    _name = "dtdream.information.shouquan.wizard"
    name= fields.Many2one("hr.employee",string="被授权人")

    @api.multi
    def _message_poss(self,approval,current_approver,next_shenpiren=None):
        approval.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">清单</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作人</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">被授权人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" %(approval.name,u'授权',current_approver.name,next_shenpiren))

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    @api.multi
    def _send_email(self,approval,current_approver,next_shenpiren):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.information.purview' % approval.id
        url = base_url+link
        appellation = next_shenpiren.name+u",您好"
        subject=current_approver.name+u"把清单为‘"+approval.name+u"’的审批权限授予你，请您尽快处理"
        content = current_approver.name+u"把清单为‘"+approval.name+u"’的审批权限授予你，请您尽快处理"
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,approval.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % next_shenpiren.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()


    #授权
    @api.multi
    def btn_submit(self):
        approval = self.env['dtdream.information.purview'].browse(self._context['active_id'])
        self._message_poss(approval=approval,current_approver=approval.current_approver,next_shenpiren=self.name.name)
        self._send_email(approval=approval,current_approver=approval.current_approver,next_shenpiren=self.name)
        approval.current_approver_user=self.name