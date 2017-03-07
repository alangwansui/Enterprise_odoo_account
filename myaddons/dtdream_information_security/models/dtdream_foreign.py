# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from openerp.osv import expression
from lxml import etree
import time
from openerp.exceptions import ValidationError

class dtdream_foreign(models.Model):
    _name = "dtdream.foreign"
    _description = u'对外披露'
    _inherit = ['mail.thread']

    @api.depends('applicant')
    def _compute_employee(self):
        for rec in self:
            rec.manager = rec.applicant.department_id.manager_id
            if rec.applicant.department_id.parent_id:
                rec.department_02 = rec.applicant.department_id
                rec.department_01 = rec.applicant.department_id.parent_id
                rec.origin_department_01 = rec.applicant.department_id.parent_id
                rec.secret_person = rec.applicant.department_id.parent_id.xinxianquanyuan
            else:
                rec.department_01 = rec.applicant.department_id
                rec.origin_department_01 = rec.applicant.department_id
                rec.secret_person = rec.applicant.department_id.xinxianquanyuan

    # @api.onchange('sfxytm')
    # def _onchange_sfxqbmxy(self):
    #     if self.sfxytm== True and not self.tminstructions:
    #         return {'warning':{
    #             'title': u'提示',
    #             'message': u'请咨询法务意见',
    #         }}

    @api.onchange('origin_department_01')
    def onchange_origin_department_01(self):
        if self.origin_department_01:
            self.secret_person = self.origin_department_01.xinxianquanyuan

    @api.constrains('target_email')
    def check_email(self):
        if self.target_email:
            import re
            str = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
            if not re.match(str, self.target_email):
                raise ValidationError(u"邮箱格式不正确")

    applicant = fields.Many2one('hr.employee', string='申请人',default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]),readonly=True)
    name=fields.Char(string="披露信息",required=True)
    department_01 = fields.Many2one("hr.department", compute=_compute_employee, string="申请人一级部门")
    department_02 = fields.Many2one("hr.department", compute=_compute_employee, string="申请人二级部门")
    origin_department_01 = fields.Many2one("hr.department", string="信息源一级部门", required=True)
    # origin_department_02 = fields.Many2one("hr.department", string="信息源二级部门")
    manager = fields.Many2one("hr.employee", string="申请人主管",required=True)
    target=fields.Char(string='披露对象',required=True,help=u'向谁披露')
    target_email = fields.Char(string='披露对象邮箱')
    # attachment = fields.Binary(string="附件(限制25M以下)", store=True)
    # attachment_name = fields.Char(string='附件名')
    url_address = fields.Char(string='链接')
    reason=fields.Text(string='披露原因',required='true')
    secret_level = fields.Selection([('level_00', '内部公开 '),('level_01', '机密'), ('level_02', '绝密')], string="最高密级", required=True)
    # sfxqbmxy=fields.Boolean(string='是否已签署保密协议')
    # bmattachment = fields.Binary(string="保密协议附件(限制25M以下)", store=True)
    # bmattachment_name = fields.Char(string='保密协议附件名')
    # sfxytm=fields.Boolean(string='是否脱敏文件')
    # tminstructions=fields.Text(string="脱敏说明")
    approves = fields.Many2many('hr.employee', string='历史审批人')
    secret_person = fields.Many2one('hr.employee', string='信息安全员',help=u'信息安全员可帮助审查对外披露信息是否满足信息安全要求（如是否添加水印，密级填写是否准确等）')
    current_approve = fields.Many2one('hr.employee', string='当前处理人')
    state = fields.Selection([('0', '草稿'),
                              ('1', '信息安全员检查'),
                              ('2', '申请人主管审批'),
                              ('3', '信息源主管审批'),
                              ('4', '权签人审批'),
                              ('-99', '不通过'),
                              ('99', '完成'),
                              ], string='状态', default='0')

    attachment_ids = fields.One2many('dtdream.foreign.attachment', 'record_id', u'附件明细')

    @api.multi
    def _compute_is_shenpiren(self):
        for rec in self:
            if self.env.user == rec.current_approve.user_id:
                rec.is_shenpiren = True
            else:
                rec.is_shenpiren = False

    is_shenpiren = fields.Boolean(string="是否审批人", compute=_compute_is_shenpiren, readonly=True)

    @api.multi
    def _compute_is_shenqingren(self):
        for rec in self:
            if self.env.user == rec.applicant.user_id:
                rec.is_shenqingren = True
            else:
                rec.is_shenqingren = False

    is_shenqingren = fields.Boolean(string="是否申请人", compute=_compute_is_shenqingren, readonly=True,default=True)



    @api.multi
    def wkf_draft(self):
        self.write({"state": '0'})
    @api.multi
    def wkf_xxyjc(self):
        self.write({"state": '1'})

    @api.multi
    def wkf_zgsp(self):
        self.write({"state": '2'})

    @api.multi
    def wkf_xxyzgsp(self):
        self.write({"state": '3'})

    @api.multi
    def wkf_qqrsp(self):
        self.write({"state": '4'})

    @api.multi
    def wkf_zz(self):
        self.write({"state": '-99'})

    @api.multi
    def wkf_wc(self):
        self.write({"state": '99'})


    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    @api.multi
    def send_email_foreign(self, next_approver):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.foreign' % self.id
        url = base_url + link
        appellation = next_approver.name + u",您好"
        subject = self.applicant.name + u"提交的‘" + self.name + u"’的对外披露申请，等待您的审批"
        content = self.applicant.name + u"提交的‘" + self.name + u"’的对外披露申请，等待您的审批"
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                             <p>%s</p>
                             <p> 请点击链接进入:
                             <a href="%s">%s</a></p>
                            <p>dodo</p>
                             <p>万千业务，简单有do</p>
                             <p>%s</p>''' % (appellation, content, url, url, self.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % next_approver.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    @api.multi
    def message_poss_foreign(self, statechange, action, next_shenpiren=None):
        next_shenpiren = next_shenpiren or u'无'
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                   <tr><th style="padding:10px">披露信息</th><th style="padding:10px">%s</th></tr>
                                                   <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                                   <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                                   <tr><td style="padding:10px">下阶段审批人</td><td style="padding:10px">%s</td></tr>
                                                   </table>""" % (self.name, statechange, action, next_shenpiren))

    @api.multi
    def message_poss_foreign_shenpi(self, statechange, action, next_shenpiren=None, reason=None):
        next_shenpiren = next_shenpiren or u'无'
        reason = reason or u'无'
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                           <tr><th style="padding:10px">披露信息</th><th style="padding:10px">%s</th></tr>
                                                           <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                                           <tr><td style="padding:10px">审批结果</td><td style="padding:10px">%s</td></tr>
                                                           <tr><td style="padding:10px">下阶段审批人</td><td style="padding:10px">%s</td></tr>
                                                           <tr><td style="padding:10px">审批意见</td><td style="padding:10px">%s</td></tr>
                                                           </table>""" % (self.name, statechange, action, next_shenpiren, reason))

    @api.constrains("attachment_ids")
    def attachment_ids_che(self):
        for attachment in self.attachment_ids:
            if not attachment.attachment:
                raise ValidationError(u'附件明细中新建记录未上传附件，请上传附件')
    @api.multi
    def do_cgtj(self):
        if self.state!="0":
            return
        if  len(self.attachment_ids)==0 and not self.url_address:
            raise ValidationError(u'附件或链接必须填写一个')

        if self.secret_person:
            self.write({'current_approve': self.secret_person.id})
            self.signal_workflow('cg_to_xxyjc')
            #发邮件   写备注
            self.message_poss_foreign(statechange=u'草稿->信息员检查', action=u'提交', next_shenpiren=self.current_approve.name)
            self.send_email_foreign(next_approver=self.current_approve)
        else:
            self.write({'current_approve': self.manager.id})
            self.signal_workflow('cg_to_zgsp')
            self.message_poss_foreign(statechange=u'草稿->主管审批', action=u'提交', next_shenpiren=self.current_approve.name)
            self.send_email_foreign(next_approver=self.current_approve)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
            if menu == u"我相关的":
                uid = self._context.get('uid', '')
                domain = expression.AND([['|', '|', '|', ('applicant.user_id', '=', uid), ('create_uid', '=', uid),
                                          ('current_approve.user_id', '=', uid), ('approves.user_id', '=', uid)],
                                         domain])
        res = super(dtdream_foreign, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                        orderby=orderby, lazy=lazy)
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
            if menu == u"我相关的":
                uid = self._context.get('uid', '')
                domain = expression.AND([['|', '|', '|', ('applicant.user_id', '=', uid), ('create_uid', '=', uid),
                                              ('current_approve.user_id', '=', uid), ('approves.user_id', '=', uid)],
                                             domain])
        return super(dtdream_foreign, self).search_read(domain=domain, fields=fields, offset=offset,limit=limit, order=order)



