# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv
from lxml import etree
from datetime import datetime


class dtdream_common_apply(models.Model):
    _name = "dtdream.common.apply"
    _description = u"邮箱申请"
    _inherit = ['mail.thread']

    apply = fields.Many2one(comodel_name="hr.employee", string=u"申请人", readonly=True, required=True,
                            default=lambda self: self.env['hr.employee'].search([('login', '=', self.env.user.login)]))
    apply_time = fields.Datetime(string=u"申请时间", readonly=True)
    approver = fields.Many2one('hr.employee', string=u'部门审批人')
    it_approver = fields.Many2one('hr.employee', string=u'IT审批人')
    users = fields.Many2many(comodel_name="hr.employee", relation="dtdream_common_group_user_rel", string=u"成员")
    is_users = fields.Boolean(string=u'是否使用users', default=False)
    description = fields.Char(string=u"描述")
    expire_time = fields.Many2one('dtdream.common.expire.time', string=u'有效期')
    state = fields.Selection([
        ("draft", u"草稿"),
        ("confirm", u"待主管审批"),
        ("acceptByMa", u"待IT审批"),
        ("acceptByIT", u"待实施"),
        ("implement", u"已完成")], string=u"状态", required=True, default="draft")
    type = fields.Many2one('dtdream.common.apply.type', string=u'申请类型', required=True, domain=[('work', '=', True)])
    opinion = fields.One2many(comodel_name="dtdream.common.opinion", inverse_name="apply_id", string=u"审批意见")
    current_approver = fields.Many2one('hr.employee', string=u'当前审批人')

    # 判断是否是部门审批人
    @api.one
    def _compute_is_approver(self):
        if self.approver.login == self.env.user.login:
            self.is_approver = True
        else:
            self.is_approver = False

    is_approver = fields.Boolean(string=u'是否是部门审批人', compute=_compute_is_approver)

    # 判断是否是IT审批人
    @api.one
    def _compute_is_it_approver(self):
        if self.it_approver.login == self.env.user.login:
            self.is_it_approver = True
        else:
            self.is_it_approver = False

    is_it_approver = fields.Boolean(string=u'是否是IT审批人', compute=_compute_is_it_approver)

    # 当前用户
    @api.one
    def _compute_current_employee(self):
        self.current_employee = self.env['hr.employee'].search([('login', '=', self.env.user.login)])[0].id

    current_employee = fields.Many2one('hr.employee', string=u'当前登录员工', compute=_compute_current_employee)


    # 显示名称
    @api.multi
    def name_get(self):
        data = []
        for r in self:
            data.append((r.id, r.type.type + u"申请"))
        return data

    @api.onchange('apply')
    def onchange_department(self):
        department = self.apply.department_id
        while department.parent_id:
            department = department.parent_id
        self.approver = department.manager_id

    @api.onchange('type')
    def onchange_employee1(self):
        self.it_approver = self.type.approver.id
        self.is_users = self.type.use_users

    @api.model
    def create(self, vals):
        if 'type' in vals:
            vals['it_approver'] = self.env['dtdream.common.apply.type'].search([('id', '=', vals['type'])])[0].approver.id
        res = super(dtdream_common_apply, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'type' in vals:
            vals['it_approver'] = self.env['dtdream.common.apply.type'].search([('id', '=', vals['type'])])[0].approver.id
        res = super(dtdream_common_apply, self).write(vals)
        return res

    # 获取邮件服务器用户邮箱作为默认发送邮箱
    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_it_man_name(self):
        result = self.env['dtdream.ad.it.man'].search([('work', '=', True)])
        names = ''
        for r in result:
            names += (r.user.nick_name + '<br/>')
        return names

    # 提醒邮件
    def send_apply_mail(self, content):
        action = self.env['ir.model.data'].search([('name', '=', 'act_dtdream_common_apply')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web?#id=%s&view_type=form&model=dtdream.common.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，您的相关申请%s，请前往查看。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>部门审批人</th>
                                    <th>IT审批人</th>
                                    <th>实施人员<th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (content, url, url, self.approver.nick_name, self.it_approver.nick_name, self.get_it_man_name()),
            'subject': u'您的相关申请%s' % content,
            'email_to': '%s' % self.apply.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 提醒部门审批人邮件
    def approver_mail(self):
        action = self.env['ir.model.data'].search([('name', '=', 'act_dtdream_common_accept')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web?#id=%s&view_type=form&model=dtdream.common.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，有待您审批的申请已提交，请前往处理。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>申请人</th>
                                    <th>申请类型</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url, self.apply.nick_name, self.type.type),
            'subject': u'有待您审批的申请已提交',
            'email_to': '%s' % self.approver.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 提醒IT审批人邮件
    def it_approver_mail(self):
        action = self.env['ir.model.data'].search([('name', '=', 'act_dtdream_common_accept')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web?#id=%s&view_type=form&model=dtdream.common.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，有待您审批的申请已通过部门审批，请前往处理。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>申请人</th>
                                    <th>申请类型</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url, self.apply.nick_name, self.type.type),
            'subject': u'有待您审批的申请已提交',
            'email_to': '%s' % self.it_approver.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    def get_it_man_mail(self):
        result = self.env['dtdream.ad.it.man'].search([('work', '=', True)])
        mail_to = ''
        for r in result:
            mail_to += (r.user.work_email + ';')
        return mail_to

    # 提醒IT实施邮件
    def it_implement_mail(self):
        action = self.env['ir.model.data'].search([('name', '=', 'act_dtdream_common_implement')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web?#id=%s&view_type=form&model=dtdream.common.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，有待您实施的申请已通过审批，请前往处理。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>申请人</th>
                                    <th>申请类型</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url, self.apply.nick_name, self.type.type),
            'subject': u'有待您实施的申请已通过审批',
            'email_to': '%s' % self.get_it_man_mail(),
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 工作流状态draft的处理
    @api.multi
    def wkf_draft(self):
        if self.state == 'confirm':
            self.send_apply_mail(u"已被部门审批人驳回")
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                        <tr><td style="padding:10px">操作</td><td style="padding:10px">时间</td></tr>
                                        <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                        </table>""" % (u'提交->驳回', fields.Datetime.now()))
        elif self.state == 'acceptByMa':
            self.send_apply_mail(u"已被IT审批人驳回")
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                        <tr><td style="padding:10px">操作</td><td style="padding:10px">时间</td></tr>
                                        <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                        </table>""" % (u'待IT审批->驳回', fields.Datetime.now()))
        elif self.state == 'acceptByIT':
            self.send_apply_mail(u"已被IT实施人驳回")
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                        <tr><td style="padding:10px">操作</td><td style="padding:10px">时间</td></tr>
                                        <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                        </table>""" % (u'待IT实施->驳回', fields.Datetime.now()))
        self.write({'state': 'draft', 'current_approver': None})

    # 工作流状态confirm的处理
    @api.multi
    def wkf_confirm(self):
        if not self.approver:
            raise osv.except_osv(u'部门审批人不能为空')
        if not self.it_approver:
            raise osv.except_osv(u'IT审批人不能为空')
        if not self.expire_time:
            raise osv.except_osv(u'有效期不能为空')
        if not self.description:
            raise osv.except_osv(u'描述不能为空')
        self.write({'state': 'confirm', 'apply_time': datetime.utcnow(), 'current_approver': self.approver.id})
        self.send_apply_mail(u"已提交，请等候部门审批")
        self.approver_mail()
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                <tr><td style="padding:10px">操作</td><td style="padding:10px">时间</td></tr>
                                <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                </table>""" % (u'草稿->提交', fields.Datetime.now()))

    # 工作流状态acceptByMa的处理
    @api.multi
    def wkf_acceptByManager(self):
        self.write({'state': 'acceptByMa', 'current_approver': self.it_approver.id})
        self.send_apply_mail(u"已通过部门审批，请等候IT审批")
        self.it_approver_mail()
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                <tr><td style="padding:10px">操作</td><td style="padding:10px">时间</td></tr>
                                <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                </table>""" % (u'提交->待IT审批', fields.Datetime.now()))

    # 工作流状态acceptByIT的处理
    @api.multi
    def wkf_acceptByIT(self):
        self.write({'state': 'acceptByIT', 'current_approver': None})
        self.send_apply_mail(u"已通过IT审批，请等候实施")
        self.it_implement_mail()
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                    <tr><td style="padding:10px">操作</td><td style="padding:10px">时间</td></tr>
                                    <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                    </table>""" % (u'待IT审批->待实施', fields.Datetime.now()))

    # 工作流状态implement的处理
    @api.multi
    def wkf_implement(self):
        self.write({'state': 'implement'})
        self.send_apply_mail(u"已通过并已实施")
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                    <tr><td style="padding:10px">操作</td><td style="padding:10px">时间</td></tr>
                                    <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                    </table>""" % (u'待实施->完成', fields.Datetime.now()))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_common_apply, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"我的申请":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
                doc.xpath("//form")[0].set("edit", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
            if res['type'] == "kanban":
                doc.xpath("//kanban")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res
