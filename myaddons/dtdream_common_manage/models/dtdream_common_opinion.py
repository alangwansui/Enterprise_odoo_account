# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime

class dtdream_common_opinion(models.Model):
    _name = "dtdream.common.opinion"
    _description = u"审批意见"

    apply_id = fields.Many2one(comodel_name="dtdream.common.apply", string=u"申请ID", readonly=True, required=True)
    stage = fields.Selection([
        ("manager", u"主管审批"),
        ("it", u"IT审批"),
        ("im", u"IT实施")], string=u"阶段", readonly=True, required=True)
    approver = fields.Many2one(comodel_name="hr.employee", string=u"审批人", readonly=True, required=True)
    result = fields.Selection([
        ("accept", u"同意"),
        ("refuse", u"驳回")], string=u"结果", default='accept', required=True)
    opinion = fields.Char(string=u"意见")

    @api.multi
    def create_opinion(self):
        if self.stage == "manager" and self.result == "accept":
            self.apply_id.signal_workflow('btn_acceptByMa')
        if self.stage == "manager" and self.result == "refuse":
            self.apply_id.signal_workflow('btn_refuseByMa')
        if self.stage == "it" and self.result == "accept":
            self.apply_id.signal_workflow('btn_acceptByIT')
        if self.stage == "it" and self.result == "refuse":
            self.apply_id.signal_workflow('btn_refuseByIT')
        if self.stage == "im" and self.result == "accept":
            self.apply_id.signal_workflow('btn_implement')
        if self.stage == "im" and self.result == "refuse":
            self.apply_id.signal_workflow('btn_refuseByIm')


class dtdream_common_expire_time(models.Model):
    _name = "dtdream.common.expire.time"
    _description = u"通用有效期"

    name = fields.Char(string=u"有效期文本", required=True)
    days = fields.Integer(string=u"有限期天数", required=True)

    # 获取邮件服务器用户邮箱作为默认发送邮箱
    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_it_man_mail(self):
        result = self.env['dtdream.ad.it.man'].search([('work', '=', True)])
        mail_to = ''
        for r in result:
            mail_to += (r.user.work_email + ';')
        return mail_to

    # 提醒IT实施邮件
    def it_implement_mail(self, aid):
        action = self.env['ir.model.data'].search([('name', '=', 'act_dtdream_common_all')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web?#id=%s&view_type=form&model=dtdream.common.apply&action=%s&menu_id=%s' % (aid.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，有%s今日到期，请处理。</p>
                                 <p><a href="%s">%s</a></p>
                                 <p>dodo</p>
                                 <p>万千业务，简单有do</p>''' % (aid.type.type, url, url),
            'subject': u'有%s今日到期了' % aid.type.type,
            'email_to': '%s' % self.get_it_man_mail(),
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 提醒申请人邮件
    def send_apply_mail(self, aid):
        action = self.env['ir.model.data'].search([('name', '=', 'act_dtdream_common_apply')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web?#id=%s&view_type=form&model=dtdream.common.apply&action=%s&menu_id=%s' % (aid.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，您的%s还有5天到期，请注意查看。</p>
                             <p><a href="%s">%s</a></p>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (aid.type.type, url, url, ),
            'subject': u'您的%s还有5天到期了' % aid.type.type,
            'email_to': '%s' % aid.apply.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    @api.model
    def timing_check(self):
        result = self.env['dtdream.common.apply'].search([('state', '=', 'implement')])
        for r in result:
            if (datetime.utcnow() - datetime.strptime(r.apply_time, '%Y-%m-%d %H:%M:%S')).days - 5 == r.expire_time.days:
                self.send_apply_mail(r)
            if (datetime.utcnow() - datetime.strptime(r.apply_time, '%Y-%m-%d %H:%M:%S')).days == r.expire_time.days:
                self.it_implement_mail(r)




