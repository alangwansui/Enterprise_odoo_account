# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
from openerp.dtdream.ldap.dtldap import DTLdap
from openerp.osv import osv

import sys

reload(sys)

sys.setdefaultencoding('utf-8')

# 域群组申请信息
class dtdream_group_apply(models.Model):
    _name = 'dtdream.group.apply'
    _description = u'域群组申请信息'
    _inherit = ['mail.thread']

    apply = fields.Many2one('hr.employee', string=u'申请人', required=True, readonly=True,
                            default=lambda self: self.env['hr.employee'].search([('login', '=', self.env.user.login)]))
    department = fields.Many2one('hr.department', string=u'域群组所属部门', required=True)
    approver = fields.Many2one('hr.employee', string='审批人', required=True)
    group = fields.Char(string=u'团队')
    label = fields.Char(string=u'域群组缩写', required=True)
    time = fields.Datetime(string=u'申请时间', required=True, readonly=True, default=datetime.utcnow())
    ext = fields.Many2one('dtdream.ad.ext', string=u'标签')
    users = fields.Many2many(comodel_name='hr.employee', relation='dtdream_ad_apply_user_rel', string=u'域群组成员')
    admins = fields.Many2many(comodel_name='hr.employee', relation='dtdream_ad_apply_admin_rel', string=u'管理员')
    expire_time = fields.Many2one('dtdream.expire.time', string=u'有效时长')
    name = fields.Char(string=u'实施域群组名称')
    description = fields.Char(string=u'描述', required=True)
    name1 = fields.Char(string=u'默认域群组名称', help=u'根据内容自动生成', readonly=True)
    name2 = fields.Char(string=u'建议域群组名称', help=u'若系统生成域群组名称不合理，请填写此名称')
    state = fields.Selection([
        ('draft', u'草稿'),
        ('confirm', u'已提交'),
        ('accept', u'已同意'),
        ('implement', u'已实施')], string=u'状态', default='draft', readonly=True)
    reason = fields.Char(string=u'驳回理由')

    # 一级部门
    def get_department(self):
        department = self.apply.department_id
        print department
        while department.parent_id:
            department = department.parent_id
            print department
        self.department = department.id

    # 显示名称
    @api.multi
    def name_get(self):
        data = []
        for r in self:
            data.append((r.id, r.name1))
        return data

    # 判断是否是审批人
    @api.one
    def _compute_is_approver(self):
        if self.approver.login == self.env.user.login:
            self.is_approver = True
        else:
            self.is_approver = False

    is_approver = fields.Boolean(string=u'是否是审批人', compute=_compute_is_approver)

    @api.onchange('apply')
    def onchange_department(self):
        department = self.apply.department_id
        while department.parent_id:
            department = department.parent_id
        self.department = department.id

    @api.onchange('department')
    def onchange_employee1(self):
        department = self.department
        while department.parent_id:
            department = department.parent_id
        self.approver = department.manager_id

    @api.onchange('department', 'label', 'ext')
    def onchange_name(self):
        array = []
        if self.department:
            department = self.department
            while department.parent_id:
                department = department.parent_id
            result = self.env['dtdream.ad.department'].search([('name', '=', department.id)])
            if result:
                array.append(result[0].value)
        if self.label:
            array.append(self.label)
        if self.ext:
            array.append(self.ext.value)
        self.name1 = ('-').join(array)

    def compute_name(self, vals):
        array = []
        if vals.has_key('department'):
            if vals['department']:
                depart = self.env['hr.department'].search([('id', '=', vals['department'])])[0]
                while depart.parent_id:
                    depart = depart.parent_id
                result = self.env['dtdream.ad.department'].search([('name', '=', depart.id)])
                array.append(result[0].value) if result else None
        elif self.department:
            depart = self.department
            while depart.parent_id:
                depart = depart.parent_id
            result = self.env['dtdream.ad.department'].search([('name', '=', depart.id)])
            array.append(result[0].value) if result else None
        if vals.has_key('label'):
            array.append(vals['label'])
        elif self.label:
            array.append(self.label)
        if vals.has_key('ext'):
            if vals['ext']:
                array.append(self.env['dtdream.ad.ext'].search([('id', '=', vals['ext'])])[0].value)
        elif self.ext:
            array.append(self.ext.value)
        return ('-').join(array)

    @api.model
    def create(self, vals):
        vals['name1'] = self.compute_name(vals)
        res = super(dtdream_group_apply, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        vals['name1'] = self.compute_name(vals)
        res = super(dtdream_group_apply, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        for admin in self.admins:
            if len(self.sudo().search([('admins','=',admin.id)]))==1:
                self.env.ref("dtdream_ad_manager.group_ad_apply_manager").sudo().write({'users': [(3,admin.user_id.id)]})
        res = super(dtdream_group_apply, self).unlink()
        return res


    # 群组修改
    def group_create(self):
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
        except Exception, e:
            raise osv.except_osv(u'ldap连接错误,请联系管理员检查公司LDAP数据配置')
        if dtldap.is_group_exist(self.name):
            raise osv.except_osv(u'域群组名称已存在，请更换')
        dtldap.create_group(self.name)
        for user in self.users:
            if dtldap.is_user_exist(user.account):
                 dtldap.add_user_to_group(user.account, self.name)
        result = self.env['dtdream.ad.group'].create({
            'name': self.name,
            'department': self.department.id,
            'time': datetime.utcnow(),
            'description': self.description,
            'work': True,
            'users': [(4, user.id) for user in self.users],
            'admins': [(4, user.id) for user in self.admins],
            'expire_time': self.expire_time.id
        })
        result.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                <tr><th style="padding:10px" colspan="2" align="center">创建域群组</th></tr>
                                                <tr><td style="padding:10px">群组名称</td></tr>
                                                <tr><td style="padding:10px">%s</td></tr>
                                                </table>""" %  result.name)
        self.create_mail(result.id)
        dtldap.unbind()

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
            mail_to +=(r.user.work_email + ';')
        return mail_to

    def get_it_man_name(self):
        result = self.env['dtdream.ad.it.man'].search([('work', '=', True)])
        names = ''
        for r in result:
            names += (r.user.nick_name + '<br/>')
        return names

    def confirm_mail(self):
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，您的域群组相关申请已提交。</p>
                                     <table border="1">
                                        <tr>
                                            <th>群组名称</th>
                                            <th>审批人</th>
                                        </tr>
                                        <tr>
                                            <td>%s</td>
                                            <td>%s</td>
                                        </tr>
                                     </table>
                                     <p>dodo</p>
                                     <p>万千业务，简单有do</p>''' % (self.name2 if self.name2 else self.name1, self.approver.nick_name),
            'subject': u'您的域群组相关申请已提交',
            'email_to': '%s' % self.apply.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

   # 同意邮件
    def accept_mail(self):
        action = self.env['ir.model.data'].search([('name', '=', 'act_ad_group_apply')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web#id=%s&view_type=form&model=dtdream.group.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，您创建域群组的申请已被同意，请前往查看。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>群组名称</th>
                                    <th>所属部门</th>
                                    <th>审批人</th>
                                    <th>实施人员</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url,  self.name2 if self.name2 else self.name1, self.department.name, self.approver.nick_name, self.get_it_man_name()),
            'subject': u'您的域群组相关申请被同意了',
            'email_to': '%s' % self.apply.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 拒绝邮件
    def refuse_mail(self):
        action = self.env['ir.model.data'].search([('name', '=', 'act_ad_group_apply')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web#id=%s&view_type=form&model=dtdream.group.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，您创建域群组的申请已被拒绝，请前往查看。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>群组名称</th>
                                    <th>所属部门</th>
                                    <th>审批人</th>
                                    <th>描述</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url,  self.name2 if self.name2 else self.name1, self.department.name, self.approver.nick_name, self.description),
            'subject': u'您的域群组相关申请被拒绝了',
            'email_to': '%s' % self.apply.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 群组创建邮件
    def create_mail(self, gid):
        action = self.env['ir.model.data'].search([('name', '=', 'act_ad_group')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web#id=%s&view_type=form&model=dtdream.ad.group&action=%s&menu_id=%s' % (gid, action, menu))
        email_list = ''
        for user in self.admins:
            email_list += (user.work_email + ';')
        self.env['mail.mail'].create({
            'body_html': u'''<p> 您好，您管理的域群组已被创建，请前往查看。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>群组名称</th>
                                    <th>所属部门</th>
                                    <th>描述</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url, self.name, self.department.name, self.description),
            'subject': u'您管理的域群组已经创建了',
            'email_to': '%s' % email_list,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 待审批邮件
    def approver_mail(self):
        action = self.env['ir.model.data'].search([('name', '=', 'act_ad_apply_approver')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web#id=%s&view_type=form&model=dtdream.group.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p> 您好，有待您审批的域群组创建申请已提交，请前往查看。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>申请人</th>
                                    <th>描述</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url, self.apply.nick_name, self.description),
            'subject': u'待您审批的域群组申请已提交',
            'email_to': '%s' % self.approver.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    def implement_mail(self, email_to):
        action = self.env['ir.model.data'].search([('name', '=', 'act_ad_apply_implement')]).res_id
        menu = self.env['ir.model.data'].search([('name', '=', 'menu_dtdream_demand_manage_root')]).res_id
        url = self.get_base_url() + ('/web#id=%s&view_type=form&model=dtdream.group.apply&action=%s&menu_id=%s' % (self.id, action, menu))
        self.env['mail.mail'].create({
            'body_html': u'''<p>您好，有待实施的域群组创建申请已提交，请前往查看。</p>
                             <p><a href="%s">%s</a></p>
                             <table border="1">
                                <tr>
                                    <th>群组名称</th>
                                    <th>所属部门</th>
                                    <th>审批人</th>
                                    <th>描述</th>
                                </tr>
                                <tr>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                    <td>%s</td>
                                </tr>
                             </table>
                             <p>dodo</p>
                             <p>万千业务，简单有do</p>''' % (url, url, self.name2 if self.name2 else self.name1, self.department.name, self.approver.nick_name, self.description),
            'subject': u'待实施的域群组创建申请已提交',
            'email_to': '%s' % email_to,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 工作流状态draft的处理
    @api.multi
    def wkf_draft(self):
        if self.state == 'confirm':
            self.refuse_mail()
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                                <tr><td style="padding:10px">操作</td><td style="padding:10px">理由</td></tr>
                                                                <tr><td style="padding:10px">%s</td><td style="padding:10px">%s</td></tr>
                                                                </table>""" % (u'拒绝', self.reason))
        self.write({'state': 'draft'})

    # 工作流状态confirm的处理
    @api.multi
    def wkf_confirm(self):
        # 添加申请人到管理员
        result = [user.login for user in self.admins]
        if self.env.user.login not in result:
            uid = self.env['hr.employee'].search([('login', '=', self.env.user.login)]).id
            self.write({'admins': [(4, uid)]})
        self.write({'state': 'confirm', 'time': datetime.utcnow()})
        self.confirm_mail()
        self.approver_mail()
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                            <tr><td style="padding:10px">操作</td></tr>
                                                            <tr><td style="padding:10px">%s</td></tr>
                                                            </table>""" % u'提交')

    # 工作流状态accept的处理
    @api.multi
    def wkf_accept(self):
        self.write({'state': 'accept'})
        self.accept_mail()
        self.implement_mail(self.get_it_man_mail())
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                            <tr><td style="padding:10px">操作</td></tr>
                                                            <tr><td style="padding:10px">%s</td></tr>
                                                            </table>""" % u'审批同意')

    # 工作流状态implement的处理
    @api.multi
    def wkf_implement(self):
        self.group_create()
        self.write({'state': 'implement'})
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                        <tr><td style="padding:10px">操作</td></tr>
                                                        <tr><td style="padding:10px">%s</td></tr>
                                                        </table>""" % u'实施')
        array = [(4, admin.user_id.id) for admin in self.admins]
        self.env.ref("dtdream_ad_manager.group_ad_apply_manager").sudo().write({'users': array})


    def act_refuse_apply(self, cr, uid, ids, context={}):
        obj = self.pool.get('ir.ui.view')
        viewID = obj.search(cr, uid, [('name', '=', 'view.dtdream.ad.apply.refuse.form')], context=context)
        return {
            'name': u"驳回理由",
            'view_mode': 'form',
            'view_id': viewID[0],
            'view_type': 'form',
            'res_model': 'dtdream.group.apply',
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }

    def act_name(self, cr, uid, ids, context={}):
        obj = self.pool.get('ir.ui.view')
        viewID = obj.search(cr, uid, [('name', '=', 'view.dtdream.ad.apply.name.form')], context=context)
        return {
            'name': u"域群组名称",
            'view_mode': 'form',
            'view_id': viewID[0],
            'view_type': 'form',
            'res_model': 'dtdream.group.apply',
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }




