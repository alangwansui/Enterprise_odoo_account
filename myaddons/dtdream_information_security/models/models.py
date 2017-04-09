# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from openerp.exceptions import ValidationError

from openerp.dtdream.ldap.dtldap import DTLdap



class dtdream_information_purview(models.Model):
    _name = 'dtdream.information.purview'
    _description = u"权限申请"
    _inherit = ['mail.thread']

    @api.depends('applicant')
    def _compute_employee(self):
        for rec in self:
            rec.manager=rec.applicant.department_id.manager_id
            if rec.applicant.department_id.parent_id:
                rec.department_02=rec.applicant.department_id
                rec.sq_department_code = rec.applicant.department_id.code
                rec.department_01=rec.applicant.department_id.parent_id
            else:
                rec.department_01=rec.applicant.department_id
                rec.sq_department_code = rec.applicant.department_id.code


    name = fields.Char(string="摘要")
    @api.constrains('origin_department_01','origin_department_02','style')
    @api.onchange('origin_department_01','origin_department_02')
    def make_name(self):
        state_list = [('conf','Confluence'),('git','Gitlab'),('other',u'其他')]
        state_dict = dict(state_list)
        style=state_dict[self.style]
        dep_01 = self.origin_department_01.name or ''
        self.write({'name':dep_01+style+u'权限'})

    @api.onchange('style')
    def on_change_style(self):
        for rec in self:
            if rec.style=='conf':
                self.conf_flag=True
                self.git_flag=False
                self.other_flag=False
                self.git_list=[(5,)]
                self.other_list = [(5,)]
            if rec.style=='git':
                self.conf_flag=False
                self.git_flag=True
                self.other_flag=False
                self.confluence_list = [(5,)]
                self.other_list = [(5,)]
            if rec.style=='other':
                self.conf_flag=False
                self.git_flag=False
                self.other_flag=True
                self.confluence_list = [(5,)]
                self.git_list = [(5,)]

    conf_flag = fields.Boolean(string="标记conf显示",default=True)
    git_flag = fields.Boolean(string="标记git显示",default=False)
    other_flag = fields.Boolean(string="标记other显示",default=False)

    style=fields.Selection([('conf','Confluence'),('git','Gitlab'),('other','其他')],string="类别",default='conf',required=True)
    confluence_list= fields.One2many("dtdream.security.list.confluence","security_conf",string="Confluence清单")
    git_list= fields.One2many("dtdream.security.list.git","security_git",string="Gitlab清单")
    other_list= fields.One2many("dtdream.security.list.other","security_other",string="Other清单")

    @api.constrains("confluence_list")
    def _constraint_conf(self):
        list = self.confluence_list
        spaceset = set([x.space for x in list])
        if len(list)!= len(spaceset):
            raise ValidationError(u"所选空间有重复")
        for lit in list:
            if not lit.read_right and not lit.write_right:
                raise ValidationError(u"请填写"+lit.space.name+u"的权限")

    applicant = fields.Many2one("hr.employee",string="申请人",required=True,store=True,default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]),readonly=True,stroe=True)
    department_01 = fields.Many2one("hr.department",compute=_compute_employee,string="申请人一级部门" ,store=True)
    department_02 = fields.Many2one("hr.department",compute=_compute_employee,string="申请人二级部门" ,store=True)
    sq_department_code = fields.Char(compute=_compute_employee,string="申请部门编码" ,store=True)
    yuan_department_code = fields.Char(string="源部门编码",readonly=True)

    #部门的联动
    @api.onchange('origin_department_02')
    def _chang_department(self):
        if self.origin_department_02:
            self.origin_department_01 = self.origin_department_02.parent_id
            self.yuan_department_code = self.origin_department_02.code
        elif self.origin_department_01:
            self.yuan_department_code = self.origin_department_01.code
        else:
            self.yuan_department_code=False

    @api.onchange('origin_department_01')
    def _chang_department_2(self):
        domain = {}
        self.origin_department_02=False
        if self.origin_department_01:
            domain['origin_department_02'] = [('parent_id', '=', self.origin_department_01.id)]
        else:
            domain['origin_department_02']= [('parent_id.parent_id', '=', False)]
        return {'domain': domain}


    origin_department_01 = fields.Many2one("hr.department",string="信息源一级部门" ,store=True,required=True)
    origin_department_02 = fields.Many2one("hr.department",string="信息源二级部门" ,store=True)
    manager = fields.Many2one("hr.employee",string="申请人主管",required=True)
    # secret_level = fields.Selection([('level_01','机密'),('level_02','绝密')],string="最高密级",required=True)
    state = fields.Selection([('state_01','草稿'),('state_02','主管审批'),('state_03','信息所有人审批'),('state_04','不通过'),('state_05','完成')],string="状态",default='state_01')
    Co_applicant = fields.Many2many("hr.employee",string="共同申请人",domain=lambda self: [("user_id", "!=", self.env.user.id)])

    reason = fields.Text(string='申请原因', required=True)

    @api.onchange('Co_applicant')
    @api.constrains('Co_applicant')
    def _depends_co_user(self):
        for rec in self:
            for appl in self.Co_applicant:
                rec.write({'Co_applicant_user': [(4,appl.user_id.id)]})
    Co_applicant_user = fields.Many2many("res.users" ,"dtdream_inf_pur_co_applicant",string="共同申请人用户",compute="_depends_co_user",store=True)


    @api.constrains('dead_line')
    @api.onchange('dead_line')
    def con_dead_line(self):
        if self.dead_line>(datetime.now() + relativedelta(years=1)).strftime("%Y-%m-%d"):
            raise ValidationError(u'期限要在一年之内')

    @api.constrains('dead_line')
    def cons_dead_line(self):
        if self.dead_line and self.dead_line<=datetime.now().strftime("%Y-%m-%d"):
            raise ValidationError(u'期限应大于今天')

    dead_line=fields.Date(string="期限",required=True)
    is_maturity = fields.Boolean(string="标记是否发过到期邮件",default=False)
    is_maturity_before = fields.Boolean(string="标记是否到期前提醒",default=False)
    is_month = fields.Boolean(string="标记申请期限是否大于一个月")
    shenqing_date = fields.Datetime(string="申请时间")


    current_approver_user = fields.Many2one("res.users",string="当前审批人用户")

    @api.depends("current_approver_user")
    def _depends_user(self):
        for rec in self:
            if rec.current_approver_user:
                em = self.env['hr.employee'].search([('user_id','=',rec.current_approver_user.id)])
                rec.current_approver=em.id
            else:
                rec.current_approver=False
    current_approver = fields.Many2one("hr.employee",compute="_depends_user",string="当前审批人")

    his_approver_user = fields.Many2many("res.users" ,"dtdream_inf_pur_his",string="历史审批人员")

    information_syr = fields.Many2one("hr.employee",string="信息所有人")

    @api.multi
    def _compute_create(self):
        for rec in self:
            if rec.create_uid==self.env.user:
                rec.is_create=True
            else:
                rec.is_create=False
    is_create = fields.Boolean(string="是否创建者",compute=_compute_create,stroe=True,default=True)

    @api.multi
    def _compute_is_shenpiren(self):
        for rec in self:
            if self.env.user in rec.current_approver_user:
                rec.is_shenpiren=True
            else:
                rec.is_shenpiren = False
    is_shenpiren = fields.Boolean(string="是否审批人",compute=_compute_is_shenpiren,readonly=True)


    #流程方法
    @api.model
    def wkf_cg(self):
        self.write({'state':'state_01'})

    @api.model
    def wkf_zgsp(self):
        self.write({'state':'state_02'})

    @api.model
    def wkf_syrsp(self):
        self.write({'state':'state_03'})

    @api.model
    def wkf_zhongzhi(self):
        self.write({'state':'state_04'})

    @api.model
    def wkf_wc(self):
        self.write({'state':'state_05'})


    @api.multi
    def _message_poss(self,statechange,action,next_shenpiren=None):
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">清单</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">下阶段审批人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" %(self.name,statechange,action,next_shenpiren))

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    @api.multi
    def _send_email(self,next_approver):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.information.purview' % self.id
        url = base_url+link
        appellation = next_approver.name+u",您好"
        subject=self.applicant.name+u"提交的权限申请，等待您的审批"
        content = self.applicant.name+u"提交的‘"+self.name+u"’的权限申请，等待您的审批"
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % next_approver.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()

    #草稿提交
    @api.multi
    def do_cgtj(self):
        if self.state!="state_01":
            return
        if self.style=="conf" and len(self.confluence_list)==0:
            raise ValidationError("明细不能为空")
        if self.style=="git" and len(self.git_list)==0:
            raise ValidationError("明细不能为空")
        if self.style=="other" and len(self.other_list)==0:
            raise ValidationError("明细不能为空")
        # if self.secret_level=="level_01":
        if not self.origin_department_01.manager_id:
            raise ValidationError(u'信息源一级部门主管不能为空')
        self.write({'information_syr':self.origin_department_01.manager_id.id,'shenqing_date':datetime.now()})
        if self.dead_line>(datetime.now() + relativedelta(months=1)).strftime("%Y-%m-%d"):
            self.write({'is_month':True})
        if self.applicant ==self.manager:
            self._message_poss(statechange=u'草稿->信息所有人审批',action=u'提交',next_shenpiren=self.information_syr.name)
            self.write({'current_approver_user': self.information_syr.user_id.id})
            self._send_email(next_approver=self.information_syr)
            self.signal_workflow('cg_to_syrsp')
        else:
            self._message_poss(statechange=u'草稿->主管审批',action=u'提交',next_shenpiren=self.manager.name)
            self.write({'current_approver_user': self.manager.user_id.id})
            self._send_email(next_approver=self.manager)
            self.signal_workflow('cg_to_zgsp')



    #权限到期提前提醒(在到期前两周邮件提醒)
    @api.model
    def timing_send_email_before(self):
        applications = self.env['dtdream.information.record'].sudo().search([])
        for application in applications:
            if application.dead_line==(datetime.now() + relativedelta(days=14)).strftime("%Y-%m-%d"):
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream.information.purview' % application.event.id
                url = base_url+link
                appellation = application.applicant.name+u",您好"
                subject=application.applicant.name+u"申请的‘"+application.event.name+u"’的权限申请还有两周到期"
                content = application.applicant.name+u"申请的‘"+application.event.name+u"’的权限申请还有两周到期，请注意！"
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,application.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % application.applicat.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()

    #权限到期提醒
    @api.model
    def timing_send_email(self):
        ldapconfig = self.env['res.company.ldap'].sudo().search([])[0]
        host = ldapconfig.ldap_server
        port = ldapconfig.ldap_port
        dn = ldapconfig.ldap_binddn
        passwd = ldapconfig.ldap_password
        ou = 'ou=DTALL'
        base = ldapconfig.ldap_base
        cacertfile = ldapconfig.ldap_cert_file
        try:
            dtldap = DTLdap(host=host, port=port, dn=dn, passwd=passwd, ou=ou, base=base, cacertfile=cacertfile)
            applications = self.env['dtdream.information.record'].sudo().search([('dead_line','<',datetime.now().strftime("%Y-%m-%d"))])
            for application in applications:
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream.information.purview' % application.event.id
                url = base_url+link
                appellation = application.applicant.name+u",您好"
                subject=application.applicant.name+u"申请的‘"+application.event.name+u"’的权限申请已到期"
                content = application.applicant.name+u"申请的‘"+application.event.name+u"’的权限申请已到期，若要继续查看请重新申请"
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,application.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % appellation.appellat.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()
                dtldap.del_user_from_group(application.applicat.account,application.ldap_group)
                appellation.sudo().unlink()
        except Exception,e:
            print u'ldap连接错误,请联系管理员检查公司LDAP数据配置'




    def create_ldap_user(self, confluence_space_name, dtldap, person):
        info = {
            'displayName': person.name,
            'mail': person.work_email,
            'physicalDeliveryOfficeName': person.department_id.name,
            'telephoneNumber': person.mobile_phone
        }
        dtldap.create_user(person.account, **info)
        dtldap.add_user_to_group(person.account, confluence_space_name)

    def add_employee_to_space_group(self,dtldap,confluence_space_name,shenqirenList):
        if dtldap.is_group_exist(confluence_space_name):
            for person in shenqirenList:
                if dtldap.is_user_exist(person.account) and not dtldap.is_user_in_group(person.account, confluence_space_name):
                    dtldap.add_user_to_group(person.account, confluence_space_name)
                elif not dtldap.is_user_exist(person.account):
                    # self.create_ldap_user(confluence_space_name, dtldap, person)
                    raise ValidationError(person.account + u'用户不合法')
                result = self.env["dtdream.information.record"].sudo().search([('applicant','=',person.id),("ldap_group",'=',confluence_space_name)])
                if len(result)>0:
                    if self.dead_line>result.dead_line:
                        result.write({'event':self.id,'dead_line':self.dead_line})
                else:
                    self.env["dtdream.information.record"].sudo().create({"event":self.id,
                        "applicant":person.id,"ldap_group":confluence_space_name,"dead_line":self.dead_line
                    })
        else:
            dtldap.create_group(confluence_space_name)
            for person in shenqirenList:
                if dtldap.is_user_exist(person.account):
                    dtldap.add_user_to_group(person.account, confluence_space_name)
                elif not dtldap.is_user_exist(person.account):
                    # self.create_ldap_user(confluence_space_name, dtldap, person)
                    raise ValidationError(person.account+u'用户不合法')
                result = self.env["dtdream.information.record"].sudo().search([('applicant','=',person.id),("ldap_group",'=',confluence_space_name)])
                if len(result)>0:
                    if self.dead_line>result.dead_line:
                        result.write({'event':self.id,'dead_line':self.dead_line})
                else:
                    self.env["dtdream.information.record"].sudo().create({"event":self.id,
                        "applicant":person.id,"ldap_group":confluence_space_name,"dead_line":self.dead_line
                    })

    #发送邮件给环境管理员配置权限
    def send_email_space_admin(self,confluence_space_mane,type,admin):
        appellation = admin.name + u",您好"
        if type =="read":
            subject = u'请您为群组'+confluence_space_mane+u'添加读权限'
        else:
            subject = u'请您为群组'+confluence_space_mane+u'添加读/写权限'

        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                             <p>%s</p>
                            <p>dodo</p>
                             <p>万千业务，简单有do</p>
                             <p>%s</p>''' % (appellation, subject, self.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % admin.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    def check_PermissionSets(self,confluence_list,dtldap,shenqirenList):
        for confluence in confluence_list:
            if confluence.read_right and not confluence.write_right:                                                    #只读权限
                confluence_space_read='conf_'+confluence.space.key+'_read'
                confluence_space_read = str(confluence_space_read)
                self.add_employee_to_space_group(dtldap,confluence_space_read,shenqirenList)
                self.send_email_space_admin(confluence_space_mane=confluence_space_read,type='read',admin=confluence.space.type.admin)
            if confluence.write_right:
                confluence_space_write='conf_'+confluence.space.key+'_write'
                confluence_space_write = str(confluence_space_write)
                self.add_employee_to_space_group(dtldap,confluence_space_write,shenqirenList)
                self.send_email_space_admin(confluence_space_mane=confluence_space_write,type='write',admin=confluence.space.type.admin)

    def check_git_PermissionSets(self,git_list,dtldap,shenqirenList):
        for git in git_list:
            for person in shenqirenList:
                if not dtldap.is_user_in_group(person.account, git.git.git_group):
                    dtldap.add_user_to_group(person.account, git.git.git_group)
                result = self.env["dtdream.information.record"].sudo().search([('applicant','=',person.id),("ldap_group",'=',git.git.git_group)])
                if len(result)>0:
                    if self.dead_line>result.dead_line:
                        result.write({'event':self.id,'dead_line':self.dead_line})
                else:
                    self.env["dtdream.information.record"].sudo().create({"event":self.id,
                        "applicant":person.id,"ldap_group":git.git.git_group,"dead_line":self.dead_line
                    })



    @api.multi
    def permission_settings(self):
        if self.style=="conf" or self.style=="git":
            shenqirenList = [self.applicant]+[x for x in self.Co_applicant]
            ldapconfig = self.env['res.company.ldap'].sudo().search([])[0]
            host = ldapconfig.ldap_domain
            port = ldapconfig.ldap_port
            dn = ldapconfig.ldap_binddn
            passwd = ldapconfig.ldap_password
            # ou = 'ou=DTALL'
            base = ldapconfig.ldap_base
            cacertfile = ldapconfig.ldap_cert_file
            try:
                dtldap = DTLdap(host=host, port=port, dn=dn, passwd=passwd, base=base, cacertfile=cacertfile)
            except Exception,e:
                raise ValidationError(u'ldap连接错误,请联系管理员检查公司LDAP数据配置')
            if self.style=="conf":
                self.check_PermissionSets(self.confluence_list,dtldap,shenqirenList)
            elif self.style=="git":
                self.check_git_PermissionSets(self.git_list,dtldap,shenqirenList)


