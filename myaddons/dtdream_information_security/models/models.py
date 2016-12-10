# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.dtdream.confluence import confluence as confluenceSer

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
    @api.constrains('origin_department_01','origin_department_02','secret_level')
    @api.onchange('origin_department_01','origin_department_02','secret_level')
    def make_name(self):
        dep_01 = self.origin_department_01.name or ''
        dep_02 = self.origin_department_02 or ''
        if dep_02:
            dep_02=u"/"+dep_02.name
        level=''
        if self.secret_level=='level_01':
            level=u'机密'
        elif self.secret_level=='level_02':
            level=u'绝密'
        self.write({'name':dep_01+dep_02+level+u'文档'})

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

    style=fields.Selection([('conf','confluence'),('git','git'),('other','其他')],string="类别",default='conf')
    confluence_list= fields.One2many("dtdream.security.list.confluence","security_conf",string="confluence清单")
    git_list= fields.One2many("dtdream.security.list.git","security_git",string="git清单")
    other_list= fields.One2many("dtdream.security.list.other","security_other",string="other清单")

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
    department_01 = fields.Many2one("hr.department",compute=_compute_employee,string="申请一级部门" ,store=True)
    department_02 = fields.Many2one("hr.department",compute=_compute_employee,string="申请二级部门" ,store=True)
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
    manager = fields.Many2one("hr.employee",string="直接主管",compute=_compute_employee ,store=True)
    secret_level = fields.Selection([('level_01','机密'),('level_02','绝密')],string="最高密级",required=True)
    state = fields.Selection([('state_01','草稿'),('state_02','主管审批'),('state_03','所有人审批'),('state_04','终止'),('state_05','完成')],string="状态",default='state_01')
    Co_applicant = fields.Many2many("hr.employee",string="共同申请人",domain=lambda self: [("user_id", "!=", self.env.user.id)])

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

    dead_line=fields.Date(string="期限",required=True)
    is_maturity = fields.Boolean(string="标记是否发过到期邮件",default=False)
    is_maturity_before = fields.Boolean(string="标记是否到期前提醒",default=False)
    is_month = fields.Boolean(string="标记申请期限是否大于一个月")



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
        if not self.manager:
            raise ValidationError(u'直接主管不能为空')
        if self.secret_level=="level_01":
            if not self.origin_department_01 or not self.origin_department_01.manager_id:
                raise ValidationError(u'最高机密为“机密”时，信息源一级部门不得为空且该部门的主管不能为空')
            self.write({'information_syr':self.origin_department_01.manager_id.id})
        elif self.secret_level=="level_02":
            specificlist = self.env['dtdream.information.people'].search([])
            specific=''
            if len(specificlist)>0:
                specific=specificlist[0]
            if not specific:
                raise ValidationError(u'请配置绝密信息审批人')
            self.write({'information_syr':specific.juemi_shenpi.id})
        if self.dead_line>(datetime.now() + relativedelta(months=1)).strftime("%Y-%m-%d"):
            self.write({'is_month':True})
        if self.applicant ==self.manager:
            self._message_poss(statechange=u'草稿->所有人审批',action=u'提交',next_shenpiren=self.information_syr.name)
            self.write({'current_approver_user': self.information_syr.user_id.id})
            self._send_email(next_approver=self.information_syr)
            self.signal_workflow('cg_to_syrsp')
        else:
            self._message_poss(statechange=u'草稿->主管审批',action=u'提交',next_shenpiren=self.manager.name)
            self.write({'current_approver_user': self.manager.user_id.id})
            self._send_email(next_approver=self.manager)
            self.signal_workflow('cg_to_zgsp')



    #权限到期提前提醒(若申请期限大于一个月，则在到期前两周邮件提醒)
    @api.model
    def timing_send_email_before(self):
        applications=self.env['dtdream.information.purview'].sudo().search([('state','=',('state_05')),('is_maturity_before','=',False),('is_maturity','=',False),('is_month','=',True)])
        for application in applications:
            if application.dead_line<=(datetime.now() + relativedelta(days=14)).strftime("%Y-%m-%d"):
                application.write({'is_maturity_before':True})
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream.information.purview' % application.id
                url = base_url+link
                appellation = application.applicant.name+u",您好"
                subject=application.applicant.name+u"申请的‘"+application.name+u"’的权限申请还有两周到期"
                content = application.applicant.name+u"申请的‘"+application.name+u"’的权限申请还有两周到期，请注意！"
                email_to=application.applicant.work_email
                for co in application.Co_applicant:
                    email_to+=';'+co.work_email
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,application.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % email_to,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()

    #权限到期提醒
    @api.model
    def timing_send_email(self):
        applications=self.env['dtdream.information.purview'].sudo().search([('state','=',('state_05')),('dead_line','<',datetime.now()),('is_maturity','=',False)])
        for application in applications:
            application.write({'is_maturity':True})
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream.information.purview' % application.id
            url = base_url+link
            appellation = application.applicant.name+u",您好"
            subject=application.applicant.name+u"申请的‘"+application.name+u"’的权限申请已到期"
            content = application.applicant.name+u"申请的‘"+application.name+u"’的权限申请已到期，若要继续查看请重新申请"
            email_to=application.applicant.work_email
            for co in application.Co_applicant:
                email_to+=';'+co.work_email
            self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                             <p>%s</p>
                             <p> 请点击链接进入:
                             <a href="%s">%s</a></p>
                            <p>dodo</p>
                             <p>万千业务，简单有do</p>
                             <p>%s</p>''' % (appellation,content, url,url,application.write_date[:10]),
                'subject': '%s' % subject,
                'email_to': '%s' % email_to,
                'email_cc':'%s' % application.information_syr.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()


    def check_PermissionSets(self,ConfluenceServer,confluence_list):
        for confluence in confluence_list:
            PermissionSets = ConfluenceServer.GetSpacePermissionSets(spacekey=confluence.space.key)
            if confluence.read_right and not confluence.write_right:                                                    #只读权限
                confluence_space_read=''
                viewPermission = [x for x in PermissionSets if x['type'] == "VIEWSPACE"]
                groupnames = [x['groupName'] for x in viewPermission[0]['spacePermissions'] if x.get('groupName')]
                if confluence_space_read in groupnames:                                                                 #权限组存在
                    print 111111111
                else:
                    print 222222222
            if confluence.write_right:
                editPermission = [x for x in PermissionSets if x['type']=="EDITSPACE"]
                groupnames = [x['groupName'] for x in editPermission[0]['spacePermissions'] if x.get('groupName')]

    @api.multi
    def permission_settings(self):
        if self.style=="conf":
            confs = set([x.conf for x in self.confluence_list])     #检查有几个confluence环境
            for conf in confs:
                try:
                    ConfluenceServer = confluenceSer.ConfluenceServer(ConfluenceURL=conf.url,login=conf.user,password=conf.passw)
                    confluence_list = [x for x in self.confluence_list if x.conf == conf]
                    self.check_PermissionSets(ConfluenceServer, confluence_list)
                except Exception, e:
                    raise ValidationError(conf.name+u"配置错误")


        elif self.style=="git":
            print 2222222222222
        else:
            print 33333333333333



    # @api.multi
    # def test(self):
        # import requests
        # url='http://confluence.dtdream.com'
        # values ={'os_username':'g0335','os_password':'DT_GQ0335'}
        # # jdata = json.dumps(values)
        # send_headers = {
        #                  'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        #                  'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        #                 'Content-type': 'application/json',
        #                  'Connection':'keep-alive',
        #                 }
        # req = requests.post(url, values, headers=send_headers)
        # get_url='http://confluence.dtdream.com/rest/api/content'
        # response = requests.get(get_url,cookies=req.cookies,headers=send_headers)

        # confluenceSpace = confluence.GetSpacePermissionsForUser(spacekey='CON',user='wx-0003')



