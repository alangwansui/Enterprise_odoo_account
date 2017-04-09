# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
from openerp.dtdream.ldap.dtldap import DTLdap
from openerp.osv import osv

# 域群组申请信息
class dtdream_change_apply(models.Model):
    _name = 'dtdream.change.apply'
    _description = u'群组修改信息'
    _inherit = ['mail.thread']

    apply = fields.Many2one('hr.employee', string=u'申请人', required=True, readonly=True,
                            default=lambda self: self.env['hr.employee'].search([('login', '=', self.env.user.login)]))
    type = fields.Selection([('1', u'添加成员'),
                             ('2', u'删除成员'),
                             ('3', u'添加管理员'),
                             ('4', u'删除管理员')], string=u'申请类型', default='1', required=True)
    time = fields.Datetime(string=u'申请时间', required=True, readonly=True, default=datetime.utcnow())
    users = fields.Many2many(comodel_name='hr.employee', relation='dtdream_change_apply_rel', string=u'用户')
    group = fields.Many2one('dtdream.ad.group', string=u'群组', required=True)
    state = fields.Selection([
        ('draft', u'草稿'),
        ('confirm', u'已提交'),
        ('implement', u'已实施')], string=u'状态', default='draft', readonly=True)
    reason = fields.Char(string=u'驳回理由')

    @api.onchange('time')
    def domain_group(self):
        group_ids = []
        result = self.env['dtdream.ad.group'].search([])
        for r in result:
            if self.env.user.login in [u.login for u in r.admins]:
                group_ids.append(r.id)
        return {'domain': {'group': [('id', 'in', group_ids)]}}

    @api.onchange('type', 'group')
    def domain_users(self):
        if not self.group:
            return {'domain': {'users': [('id', 'in', [])]}}
        if self.type == '1':
            user_ids = [u.id for u in self.group.users]
            return {'domain': {'users': [('id', 'not in', user_ids)]}}
        elif self.type == '2':
            user_ids = [u.id for u in self.group.users]
            return {'domain': {'users': [('id', 'in', user_ids)]}}
        elif self.type == '3':
            user_ids = [u.id for u in self.group.admins]
            return {'domain': {'users': [('id', 'not in', user_ids)]}}
        elif self.type == '4':
            user_ids = [u.id for u in self.group.admins]
            return {'domain': {'users': [('id', 'in', user_ids)]}}

    # 显示名称
    @api.multi
    def name_get(self):
        data = []
        for r in self:
            data.append((r.id, r.group.name))
        return data

    # 群组修改
    def group_change(self):
        try:
            ldapconfig = self.env['res.company.ldap'].sudo().search([])[0]
            #host = ldapconfig.ldap_server
            host = ldapconfig.ldap_domain
            port = ldapconfig.ldap_port
            dn = ldapconfig.ldap_binddn
            passwd = ldapconfig.ldap_password
            ou = 'ou=DTALL'
            base = ldapconfig.ldap_base
            cacertfile = ldapconfig.ldap_cert_file
            dtldap = DTLdap(host=host, port=port, dn=dn, passwd=passwd, ou=ou, base=base, cacertfile=cacertfile)
            result = self.group
            if self.type == '1':
                for user in self.users:
                    if dtldap.is_user_exist(user.account) and not dtldap.is_user_in_group(user.account, result.name):
                        dtldap.add_user_to_group(user.account, result.name)
                result.write({'users': [(4, user.id) for user in self.users]})
                users = ''
                for u in self.users:
                    users += (u.nick_name + '<br/>')
                result.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                   <tr><th style="padding:10px" colspan="3" align="center">添加成员</th></tr>
                                                   <tr><td style="padding:10px">群组名称</td><td style="padding:10px">添加成员</td><td style="padding:10px">时间</td></tr>
                                                   <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                                   </table>""" % (result.name, users, fields.Datetime.now()))
            elif self.type == '2':
                for user in self.users:
                    if dtldap.is_user_exist(user.account) and dtldap.is_user_in_group(user.account, result.name):
                        dtldap.del_user_from_group(user.account, result.name)
                result.write({'users': [(3, user.id) for user in self.users]})
                users = ''
                for u in self.users:
                    users += (u.nick_name + '<br/>')
                result.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                    <tr><th style="padding:10px" colspan="3" align="center">删除成员</th></tr>
                                                    <tr><td style="padding:10px">群组名称</td><td style="padding:10px">删除成员</td><td style="padding:10px">时间</td></tr>
                                                   <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                                   </table>""" % (result.name, users, fields.Datetime.now()))
            elif self.type == '3':
                result.write({'admins': [(4, user.id) for user in self.users]})
                users = ''
                for u in self.users:
                    users += (u.nick_name + '<br/>')
                result.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                    <tr><th style="padding:10px" colspan="3" align="center">添加管理员</th></tr>
                                                    <tr><td style="padding:10px">群组名称</td><td style="padding:10px">添加管理员</td><td style="padding:10px">时间</td></tr>
                                                   <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                                   </table>""" % (result.name, users, fields.Datetime.now()))
            elif self.type == '4':
                result.write({'admins': [(3, user.id) for user in self.users]})
                users = ''
                for u in self.users:
                    users += (u.nick_name + '<br/>')
                result.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                    <tr><th style="padding:10px" colspan="3" align="center">添加成员</th></tr>
                                                    <tr><td style="padding:10px">群组名称</td><td style="padding:10px">删除管理员</td><td style="padding:10px">时间</td></tr>
                                                    <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                                    </table>""" % (result.name, users, fields.Datetime.now()))
            self.accept_refuse_mail()
            self.user_change_mail(result.id)
            dtldap.unbind()
        except Exception,e:
            raise osv.except_osv(u'ldap连接错误,请联系管理员检查公司LDAP数据配置')

    # 获取邮件服务器用户邮箱作为默认发送邮箱
    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    def get_it_man_mail(self):
        result = self.env['dtdream.ad.it.man'].search([('work', '=', True)])
        mail_to = ''
        for r in result:
            mail_to +=(r.user.work_email + ';')
        return mail_to

    def get_it_man_name(self):
        result = self.env['dtdream.ad.it.man'].search([('work', '=', True)])
        names = ''
        for r in result:
            names += (r.user.nick_name + '<br/>')
        return names

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def type_change(self, type):
        array = {
            '1': u'添加成员',
            '2': u'删除成员',
            '3': u'添加管理员',
            '4': u'删除管理员'
        }
        return array[type]

    def confirm_mail(self):
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，您的域群组相关申请已提交。</p>
                                     <table border="1">
                                        <tr>
                                            <th>群组名称</th>
                                            <th>申请类型</th>
                                            <th>处理人</th>
                                        </tr>
                                        <tr>
                                            <td>%s</td>
                                            <td>%s</td>
                                            <td>%s</td>
                                        </tr>
                                     </table>
                                     <p>dodo</p>
                                     <p>万千业务，简单有do</p>''' % (self.group.name, self.type_change(self.type), self.get_it_man_name()),
            'subject': u'您的域群组相关申请已提交',
            'email_to': '%s' % self.apply.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 申请通过和拒绝邮件
    def accept_refuse_mail(self):
        action = self.env['ir.model.data'].search([('name', '=', 'act_ad_change_apply')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web#id=%s&view_type=form&model=dtdream.change.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        result = u'完成' if self.state == 'implement' else u'拒绝'
        person = ''
        for user in self.users:
            person += (user.nick_name + '<br/>')
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，您关于域群组的相关申请已被%s，请前往查看。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>群组名称</th>
                                    <th>申请类型</th>
                                    <th>涉及人员</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (result, url, url, self.group.name, self.type_change(self.type), person),
            'subject': u'您的域群组相关申请被%s了' % result,
            'email_to': '%s' % self.apply.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 成员变化邮件
    def user_change_mail(self, gid):
        action = self.env['ir.model.data'].search([('name', '=', 'act_ad_group')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web#id=%s&view_type=form&model=dtdream.ad.group&action=%s&menu_id=%s' % (gid, action, menu))
        email_list = ''
        for user in self.group.admins:
            email_list += (user.work_email + ';')
        person = ''
        for user in self.users:
            person += (user.nick_name + '<br/>')
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，您管理的域群组成员发生变化，请前往查看。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>群组名称</th>
                                    <th>类型</th>
                                    <th>成员</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url, self.group.name, self.type_change(self.type), person),
            'subject': u'您管理的域群组成员发生变化',
            'email_to': '%s' % email_list,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    def implement_mail(self, email_to):
        action = self.env['ir.model.data'].search([('name', '=', 'act_ad_change_implement')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web#id=%s&view_type=form&model=dtdream.change.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        person = ''
        for user in self.users:
            person += (user.nick_name + '<br/>')
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，有待处理的域群组修改申请已提交，请前往查看。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>群组名称</th>
                                    <th>类型</th>
                                    <th>成员</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url, self.group.name, self.type_change(self.type), person),
            'subject': u'待实施的域群组变化申请已提交',
            'email_to': '%s' % email_to,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 工作流状态draft的处理
    @api.multi
    def wkf_draft01(self):
        if self.state == 'confirm':
            self.accept_refuse_mail()
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                                <tr><td style="padding:10px">操作</td><td style="padding:10px">理由</td><td style="padding:10px">时间</td></tr>
                                                                <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                                                </table>""" % (u'拒绝', self.reason, fields.Datetime.now()))
        self.write({'state': 'draft'})


    # 工作流状态confirm的处理
    @api.multi
    def wkf_confirm01(self):
        self.write({'state': 'confirm', 'time': datetime.utcnow()})
        self.implement_mail(self.get_it_man_mail())
        self.confirm_mail()
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                            <tr><td style="padding:10px">操作</td><td style="padding:10px">时间</td></tr>
                                                            <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                                            </table>""" % (u'提交', fields.Datetime.now()))

    # 工作流状态implement的处理
    @api.multi
    def wkf_implement01(self):
        self.group_change()
        self.write({'state': 'implement'})
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                                    <tr><td style="padding:10px">操作</td><td style="padding:10px">时间</td></tr>
                                                                    <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                                                    </table>""" % (u'实施', fields.Datetime.now()))

    def act_refuse_change(self, cr, uid, ids, context={}):
        obj = self.pool.get('ir.ui.view')
        viewID = obj.search(cr, uid, [('name', '=', 'view.dtdream.ad.change.refuse.form')], context=context)
        return {
            'name': u"驳回理由",
            'view_mode': 'form',
            'view_id': viewID[0],
            'view_type': 'form',
            'res_model': 'dtdream.change.apply',
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }



