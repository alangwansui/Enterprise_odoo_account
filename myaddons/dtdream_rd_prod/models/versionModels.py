# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError

#版本
class dtdream_rd_version(models.Model):
    _name = 'dtdream_rd_version'
    _inherit =['mail.thread']
    _rec_name = 'version_numb'
    version_numb = fields.Char("版本号",required=True,track_visibility='onchange')
    @api.onchange('proName')
    def _get_pro(self):
        self.name = self.proName.name

    name=fields.Char(string="产品名称")
    proName = fields.Many2one("dtdream_prod_appr" ,required=True)


    pro_flag = fields.Selection([('flag_06','正式版本'),('flag_01','内部测试版本'),('flag_02','外部测试版本'),('flag_03','公测版本'),
                                ('flag_04','演示版本'),('flag_05','补丁版本')],
                             '版本标识',track_visibility='onchange')
    version_state = fields.Selection([
        ('draft','草稿'),
        ('initialization','计划中'),
        ('Development','开发中'),
        ('pending','待发布'),
        ('pause','暂停'),
        ('stop','中止'),
        ('released','已发布')],
        '版本状态',default="draft",track_visibility='onchange')

    version_state_old = fields.Selection([
        ('draft','草稿'),
        ('initialization','计划中'),
        ('Development','开发中'),
        ('pending','待发布'),
        ('pause','暂停'),
        ('stop','中止'),
        ('released','已发布')],
        )
    plan_dev_time = fields.Date("计划开发开始时间",help="版本开始时间指迭代开发开始时间",track_visibility='onchange')
    plan_check_pub_time = fields.Date("计划开发完成时间",track_visibility='onchange')
    plan_pub_time = fields.Date("计划发布完成时间",track_visibility='onchange')
    plan_mater=fields.Text("版本计划材料",track_visibility='onchange')

    actual_dev_time = fields.Date("实际开发开始时间",help="版本开始时间指迭代开发开始时间",track_visibility='onchange')
    dev_mater = fields.Text("版本开发材料",track_visibility='onchange')

    actual_check_pub_time =fields.Date("实际验证发布开始时间",track_visibility='onchange')
    actual_pub_time = fields.Date("实际发布完成时间",track_visibility='onchange')
    place = fields.Char('版本存放位置',track_visibility='onchange')
    Material =fields.Text('版本发布材料',track_visibility='onchange')

    @api.model
    def _compute_create(self):
        if self.create_uid==self.env.user:
            self.is_create=True
        else:
            self.is_create=False
    is_create = fields.Boolean(string="是否创建者",compute=_compute_create,stroe=True,default=True)

    @api.model
    def _compute_is_Qa(self):
        users =  self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users
        ids = []
        for user in users:
            ids+=[user.id]
        if self.env.user.id in ids:
            self.is_Qa = True
        else:
            self.is_Qa=False
    is_Qa = fields.Boolean(string="是否在QA组",compute=_compute_is_Qa,readonly=True)

    @api.model
    def _compute_is_shenpiren(self):
        if self.env.user in self.current_approver_user:
            self.is_shenpiren=True
        else:
            self.is_shenpiren = False
    is_shenpiren = fields.Boolean(string="是否审批人",compute=_compute_is_shenpiren,readonly=True)

    #返回上一部
    @api.multi
    def do_back(self):
        if self.version_state=='initialization':
            self.signal_workflow('jihuazhong_to_caogao')
        if self.version_state=='Development':
            self.signal_workflow('kaifa_to_draft')
        if self.version_state=='pending':
            self.signal_workflow('dfb_to_kaifa')
        if self.version_state=='released':
            self.signal_workflow('yfb_to_dfb')


    @api.model
    def wkf_draft(self):
        if self.version_state=='initialization':
            self.write({'is_click_01':False,'is_finish_01':False})
            processes01 = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',self.id)])
            processes01.unlink()
        self.write({'version_state': 'draft'})


    @api.model
    def wkf_jihuazhong(self):
        if self.version_state=='Development':
            self.write({'is_click_01':False,'is_click_02':False,'is_finish_01':False,'is_finish_02':False})
            processes01 = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',self.id)])
            processes01.unlink()
            processes02 = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',self.id)])
            processes02.unlink()
        # if self.version_state=='pending':
        #     self.write({'is_click_01':False,'is_click_02':False,'is_click_03':False,'is_finish_01':False,'is_finish_02':False,'is_finish_03':False})
        #     processes01 = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',self.id)])
        #     processes01.unlink()
        #     processes02 = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',self.id)])
        #     processes02.unlink()
        #     processes03 = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id)])
        #     processes03.unlink()
        self.write({'version_state': 'initialization'})

    @api.model
    def wkf_kaifa(self):
        if self.version_state=='pending':
            self.write({'is_click_02':False,'is_click_03':False,'is_finish_02':False,'is_finish_03':False})
            processes02 = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',self.id)])
            processes02.unlink()
            processes03 = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id)])
            processes03.unlink()
        self.write({'version_state': 'Development'})

    @api.model
    def wkf_dfb(self):
        if self.version_state=='released':
            self.write({'is_click_03':False,'is_finish_03':False})
            processes03 = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id)])
            processes03.unlink()
        self.write({'version_state': 'pending'})

    @api.model
    def wkf_yfb(self):
        self.write({'version_state': 'released'})

    process_01_ids = fields.One2many('dtdream_rd_process_ver','process_01_id',string='审批意见')            #计划中状态审批意见
    process_02_ids = fields.One2many('dtdream_rd_process_ver','process_02_id',string='审批意见')            #开发状态审批意见
    process_03_ids = fields.One2many('dtdream_rd_process_ver','process_03_id',string='审批意见')            #待发布状态审批意见

    is_click_01 = fields.Boolean(string="计划状态提交")
    is_click_02 = fields.Boolean(string="开发中状态提交")
    is_click_03 = fields.Boolean(string="待发布状态提交")

    is_finish_01 = fields.Boolean(string="计划状态多人审批是否完成")
    is_finish_02 = fields.Boolean(string="开发中状态多人审批是否完成")
    is_finish_03 = fields.Boolean(string="待发布状态多人审批是否完成")

    current_approver_user = fields.Many2many("res.users", "ver_c_a_u_u",string="当前审批人用户")

    his_app_user = fields.Many2many("res.users" ,"ver_h_a_u_u",string="历史审批人用户")

    @api.constrains('message_follower_ids')
    def _compute_follower(self):
        self.followers_user = False
        for foll in self.message_follower_ids:
            self.write({'followers_user': [(4,foll.partner_id.user_ids.id)]})

    followers_user = fields.Many2many("res.users" ,"ver_f_u_u",string="关注者")

    @api.multi
    def _compute_dept(self):
        em = self.env['hr.employee'].search([('user_id','=',self.env.uid)])
        if em.department_id.id == self.proName.department.id or em.department_id.id==self.proName.department_2.id:
            self.sameDept=True
        else:
            self.sameDept=False
    sameDept = fields.Boolean(compute = _compute_dept)

    def add_follower(self, cr, uid, ids, employee_id, context=None):
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        if employee and employee.user_id:
            self.message_subscribe_users(cr, uid, ids, user_ids=[employee.user_id.id], context=context)

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True, mail_create_nosubscribe=True)
        prod_id = super(dtdream_rd_version, self).create(cr, uid, values, context=context)
        self.message_subscribe_users(cr, uid, [prod_id], user_ids=[uid], context=context)
        pro = self.pool.get('dtdream_prod_appr').browse(cr,uid,values['proName'])
        rold_ids = pro.role_ids
        for rold in rold_ids:
            if rold.person:
                self.add_follower(cr, uid, [prod_id], rold.person.id, context=context)
        return prod_id

    @api.constrains('process_01_ids')
    def con_pro_01_ids(self):
        for rec in self.process_01_ids:
            if rec.is_refuse and not rec.reason :
                raise ValidationError("不通过时，意见为必填项")
        for process in self.process_01_ids:
            if process.approver_old and process.approver!=process.approver_old:
                if self.proName.department_2:
                    subject=process.approver_old.name+u"把"+self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                    content = process.approver_old.name+u"把"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                else:
                    subject=process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                    content = process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                appellation = process.approver.name+u",您好"

                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
                url = base_url+link
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % process.approver.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()
                self.message_post(body=process.approver_old.name+u'将审批权限授给'+process.approver.name)
                process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                self.add_follower(employee_id=process.approver.id)
                self.write({'current_approver_user': [(4,process.approver.user_id.id)]})
        if self.version_state=='initialization':
            for user in self.current_approver_user:
                self.write({'his_app_user': [(4, user.id)]})
            self.is_finish_01 = True
            processes = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',self.id),('ver_state','=',self.version_state),('is_new','=',True),('level','=','level_01')])

            for process in processes:
                if self.is_Qa:
                    process_01 = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',self.id),('ver_state','=',self.version_state),('is_new','=',True),('level','=','level_02')])
                    if len(process_01)==0:
                        if process.is_pass:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:通过')
                        if process.is_risk:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:带风险通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:带风险通过')
                        if process.is_refuse:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:不通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:不通过')
                else:
                    if process.approver.user_id.id == self.env.user.id:
                        if process.is_pass:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:通过')
                        if process.is_risk:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:带风险通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:带风险通过')
                        if process.is_refuse:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:不通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在计划中阶段一级审批意见:不通过')


            for process in processes:
                if not (process.is_pass or process.is_risk):
                    self.is_finish_01 = False
                    break
            if self.is_finish_01 and self.is_click_01:
                process_01 = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',self.id),('ver_state','=',self.version_state),('is_new','=',True),('level','=','level_02')])
                if len(process_01)==0:
                    self.current_approver_user = [(5,)]
                    records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',self.version_state),('level','=','level_02')])           #版本审批配置
                    rold_ids = []
                    for record in records:
                        rold_ids +=[record.name.id]
                    appro = self.env['dtdream_rd_role'].search([('role_id','=',self.proName.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                    if len(appro)==0:
                        self.signal_workflow('btn_to_dfb')
                    else:
                        for record in appro:
                            self.add_follower(employee_id=record.person.id)
                            self.env['dtdream_rd_process_ver'].create({"role":record.cof_id.id, "process_01_id":self.id,'ver_state':self.version_state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_02'})       #审批意见记录创建
                            self.write({'current_approver_user': [(4, record.person.user_id.id)]})
                            if self.proName.department_2:
                                subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，待您审批"
                            else:
                                subject=self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，待您审批"
                            appellation = record.person.name+u",您好"
                            content = self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本已进入计划中阶段，等待您的审批"
                            base_url = self.get_base_url()
                            link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
                            url = base_url+link
                            self.env['mail.mail'].create({
                                'body_html': u'''<p>%s</p>
                                             <p>%s</p>
                                             <p> 请点击链接进入:
                                             <a href="%s">%s</a></p>
                                            <p>dodo</p>
                                             <p>万千业务，简单有do</p>
                                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                                'subject': '%s' % subject,
                                'email_to': '%s' % record.person.work_email,
                                'auto_delete': False,
                                'email_from':self.get_mail_server_name(),
                            }).send()
                else:
                    for process in process_01:
                        if process.approver_old and process.approver!=process.approver_old:
                            if self.proName.department_2:
                                subject=process.approver_old.name+u"把"+self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                                content = process.approver_old.name+u"把"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                            else:
                                subject=process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                                content = process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                            appellation = process.approver.name+u",您好"
                            base_url = self.get_base_url()
                            link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
                            url = base_url+link
                            self.env['mail.mail'].create({
                                'body_html': u'''<p>%s</p>
                                             <p>%s</p>
                                             <p> 请点击链接进入:
                                             <a href="%s">%s</a></p>
                                            <p>dodo</p>
                                             <p>万千业务，简单有do</p>
                                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                                'subject': '%s' % subject,
                                'email_to': '%s' % process.approver.work_email,
                                'auto_delete': False,
                                'email_from':self.get_mail_server_name(),
                            }).send()
                            self.message_post(body=process.approver_old.name+u'将审批权限授给'+process.approver.name)
                            process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                            self.add_follower(employee_id=process.approver.id)
                        self.write({'current_approver_user': [(4, process.approver.user_id.id)]})
                    for user in self.current_approver_user:
                        self.write({'his_app_user': [(4, user.id)]})
                    if process_01.is_pass or process_01.is_risk:
                        self.signal_workflow('btn_to_kaifa')
                        self.write({'is_click_01':False})
                        if process_01.is_pass:
                            if process_01.reason:
                                self.message_post(body=process_01.approver.name+u'在计划中阶段二级审批意见:通过,原因：'+process_01.reason)
                            else:
                                self.message_post(body=process_01.approver.name+u'在计划中阶段二级审批意见:通过')
                        if process_01.is_risk:
                            if process_01.reason:
                                self.message_post(body=process_01.approver.name+u'在计划中阶段二级审批意见:带风险通过,原因：'+process_01.reason)
                            else:
                                self.message_post(body=process_01.approver.name+u'在计划中阶段二级审批意见:带风险通过')
                    elif process_01.is_refuse:
                        self.message_post(body=process_01.approver.name+u'在计划中阶段二级审批不同意，原因:'+process_01.reason)
                        proces_01all = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',self.id),('ver_state','=',self.version_state)])
                        proces_01all.unlink()
                        self.write({'is_click_01':False,'is_finish_01':False})


    @api.constrains('process_02_ids')
    def con_pro_02_ids(self):
        for rec in self.process_02_ids:
            if rec.is_refuse and not rec.reason :
                raise ValidationError("不通过时，意见为必填项")
        for process in self.process_02_ids:
            if process.approver_old and process.approver!=process.approver_old:
                if self.proName.department_2:
                    subject=process.approver_old.name+u"把"+self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                    content = process.approver_old.name+u"把"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                else:
                    subject=process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                    content = process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                appellation = process.approver.name+u",您好"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
                url = base_url+link
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % process.approver.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()
                self.message_post(body=process.approver_old.name+u'将审批权限授给'+process.approver.name)
                process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                self.add_follower(employee_id=process.approver.id)
                self.write({'current_approver_user': [(4,process.approver.user_id.id)]})
        if self.version_state=='Development':
            processes = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',self.id),('ver_state','=',self.version_state),('is_new','=',True),('level','=','level_01')])
            for process in processes:
                if self.is_Qa:
                    process_02 = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',self.id),('ver_state','=',self.version_state),('is_new','=',True),('level','=','level_02')])
                    if len(process_02)==0:
                        if process.is_pass:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:通过')
                        if process.is_risk:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:带风险通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:带风险通过')
                        if process.is_refuse:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:不通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:不通过')
                else:
                    if process.approver.user_id.id == self.env.user.id:
                        if process.is_pass:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:通过')
                        if process.is_risk:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:带风险通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:带风险通过')
                        if process.is_refuse:
                            if process.reason:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:不通过,原因：'+process.reason)
                            else:
                                self.message_post(body=process.approver.name+u'在开发中阶段一级审批意见:不通过')
            for user in self.current_approver_user:
                self.write({'his_app_user': [(4, user.id)]})
            self.is_finish_02 = True
            for process in processes:
                if not (process.is_pass or process.is_risk):
                    self.is_finish_02 = False
                    break
            if self.is_finish_02 and self.is_click_02:
                process_02 = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',self.id),('ver_state','=',self.version_state),('is_new','=',True),('level','=','level_02')])
                if len(process_02)==0:
                    self.current_approver_user = [(5,)]
                    records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',self.version_state),('level','=','level_02')])           #版本审批配置
                    rold_ids = []
                    for record in records:
                        rold_ids +=[record.name.id]
                    appro = self.env['dtdream_rd_role'].search([('role_id','=',self.proName.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                    if len(appro)==0:
                        self.signal_workflow('btn_to_dfb')
                    else:
                        for record in appro:
                            self.add_follower(employee_id=record.person.id)
                            self.env['dtdream_rd_process_ver'].create({"role":record.cof_id.id, "process_02_id":self.id,'ver_state':self.version_state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_02'})       #审批意见记录创建
                            self.write({'current_approver_user': [(4, record.person.user_id.id)]})
                            if self.proName.department_2:
                                subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，待您审批"
                            else:
                                subject=self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，待您审批"
                            appellation = record.person.name+u",您好"
                            content = self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本已进入开发中阶段，等待您的审批"
                            base_url = self.get_base_url()
                            link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
                            url = base_url+link
                            self.env['mail.mail'].create({
                                'body_html': u'''<p>%s</p>
                                             <p>%s</p>
                                             <p> 请点击链接进入:
                                             <a href="%s">%s</a></p>
                                            <p>dodo</p>
                                             <p>万千业务，简单有do</p>
                                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                                'subject': '%s' % subject,
                                'email_to': '%s' % record.person.work_email,
                                'auto_delete': False,
                                'email_from':self.get_mail_server_name(),
                            }).send()
                else:
                    for process in process_02:
                        if process.approver_old and process.approver!=process.approver_old:
                            if self.proName.department_2:
                                subject=process.approver_old.name+u"把"+self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                                content = process.approver_old.name+u"把"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                            else:
                                subject=process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                                content = process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                            appellation = process.approver.name+u",您好"
                            base_url = self.get_base_url()
                            link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
                            url = base_url+link
                            self.env['mail.mail'].create({
                                'body_html': u'''<p>%s</p>
                                             <p>%s</p>
                                             <p> 请点击链接进入:
                                             <a href="%s">%s</a></p>
                                            <p>dodo</p>
                                             <p>万千业务，简单有do</p>
                                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                                'subject': '%s' % subject,
                                'email_to': '%s' % process.approver.work_email,
                                'auto_delete': False,
                                'email_from':self.get_mail_server_name(),
                            }).send()
                            self.message_post(body=process.approver_old.name+u'将审批权限授给'+process.approver.name)
                            process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                            self.add_follower(employee_id=process.approver.id)
                            self.write({'current_approver_user': [(4, process.approver.user_id.id)]})
                    for user in self.current_approver_user:
                        self.write({'his_app_user': [(4, user.id)]})
                    if process_02.is_pass or process_02.is_risk:
                        self.signal_workflow('btn_to_dfb')
                        self.write({'is_click_02':False})
                        if process_02.is_pass:
                            if process_02.reason:
                                self.message_post(body=process_02.approver.name+u'在开发中阶段二级审批意见:通过,原因：'+process_02.reason)
                            else:
                                self.message_post(body=process_02.approver.name+u'在开发中阶段二级审批意见:通过')
                        if process_02.is_risk:
                            if process_02.reason:
                                self.message_post(body=process_02.approver.name+u'在开发中阶段二级审批意见:带风险通过,原因：'+process_02.reason)
                            else:
                                self.message_post(body=process_02.approver.name+u'在开发中阶段二级审批意见:带风险通过')
                    elif process_02.is_refuse:
                        self.message_post(body=process_02.approver.name+u'在开发中阶段二级审批不同意，原因:'+process_02.reason)
                        # self.signal_workflow('kaifa_to_draft')
                        self.write({'is_click_02':False})
                        proces_02all = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',self.id),('ver_state','=',self.version_state)])
                        proces_02all.unlink()
                        self.write({'is_click_02':False,'is_finish_02':False})

    @api.constrains('process_03_ids')
    def con_pro_03_ids(self):
        for rec in self.process_03_ids:
            if rec.is_refuse and not rec.reason :
                raise ValidationError("不通过时，意见为必填项")
        processes = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id),('ver_state','=',self.version_state),('level','=','level_01'),('is_new','=',True)])
        for process in processes:
            if self.is_Qa:
                process_03 = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id),('ver_state','=',self.version_state),('is_new','=',True),('level','=','level_02')])
                if len(process_03)==0:
                    if process.is_pass:
                        if process.reason:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:通过,原因：'+process.reason)
                        else:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:通过')
                    if process.is_risk:
                        if process.reason:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:带风险通过,原因：'+process.reason)
                        else:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:带风险通过')
                    if process.is_refuse:
                        if process.reason:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:不通过,原因：'+process.reason)
                        else:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:不通过')
            else:
                if process.approver.user_id.id == self.env.user.id:
                    if process.is_pass:
                        if process.reason:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:通过,原因：'+process.reason)
                        else:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:通过')
                    if process.is_risk:
                        if process.reason:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:带风险通过,原因：'+process.reason)
                        else:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:带风险通过')
                    if process.is_refuse:
                        if process.reason:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:不通过,原因：'+process.reason)
                        else:
                            self.message_post(body=process.approver.name+u'在待发布阶段一级审批意见:不通过')
        for process in processes:
            if process.approver_old and process.approver!=process.approver_old:
                if self.proName.department_2:
                    subject=process.approver_old.name+u"把"+self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                    content = process.approver_old.name+u"把"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                else:
                    subject=process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                    content = process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                appellation = process.approver.name+u",您好"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
                url = base_url+link
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % process.approver.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()
                self.message_post(body=process.approver_old.name+u'将审批权限授给'+process.approver.name)
                process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                self.add_follower(employee_id=process.approver.id)
                self.write({'current_approver_user': [(4,process.approver.user_id.id)]})
        if self.version_state=='pending':
            for user in self.current_approver_user:
                self.write({'his_app_user': [(4, user.id)]})
            self.is_finish_03 = True
            for process in processes:
                if not (process.is_pass or process.is_risk):
                    self.is_finish_03 = False
                    break
            if self.is_finish_03 and self.is_click_03:
                process_03 = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id),('ver_state','=',self.version_state),('is_new','=',True),('level','=','level_02')])
                if len(process_03)==0:
                    self.current_approver_user = [(5,)]
                    records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',self.version_state),('level','=','level_02')])           #版本审批配置
                    rold_ids = []
                    for record in records:
                        rold_ids +=[record.name.id]
                    appro = self.env['dtdream_rd_role'].search([('role_id','=',self.proName.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                    if len(appro)==0:
                        self.signal_workflow('btn_to_yfb')
                    else:
                        for record in appro:
                            self.add_follower(employee_id=record.person.id)
                            self.env['dtdream_rd_process_ver'].create({"role":record.cof_id.id, "process_03_id":self.id,'ver_state':self.version_state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_02'})       #审批意见记录创建
                            self.write({'current_approver_user': [(4, record.person.user_id.id)]})
                            if self.proName.department_2:
                                subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，待您审批"
                            else:
                                subject=self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，待您审批"
                            appellation = record.person.name+u",您好"
                            content = self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本已进入待发布阶段，等待您的审批"
                            base_url = self.get_base_url()
                            link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
                            url = base_url+link
                            self.env['mail.mail'].create({
                                'body_html': u'''<p>%s</p>
                                             <p>%s</p>
                                             <p> 请点击链接进入:
                                             <a href="%s">%s</a></p>
                                            <p>dodo</p>
                                             <p>万千业务，简单有do</p>
                                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                                'subject': '%s' % subject,
                                'email_to': '%s' % record.person.work_email,
                                'auto_delete': False,
                                'email_from':self.get_mail_server_name(),
                            }).send()
                else:
                    for process in process_03:
                        if process.approver_old and process.approver!=process.approver_old:
                            if self.proName.department_2:
                                subject=process.approver_old.name+u"把"+self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                                content = process.approver_old.name+u"把"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                            else:
                                subject=process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                                content = process.approver_old.name+u"把"+self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"版本，审批权限授予你"
                            appellation = process.approver.name+u",您好"
                            base_url = self.get_base_url()
                            link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
                            url = base_url+link
                            self.env['mail.mail'].create({
                                'body_html': u'''<p>%s</p>
                                             <p>%s</p>
                                             <p> 请点击链接进入:
                                             <a href="%s">%s</a></p>
                                            <p>dodo</p>
                                             <p>万千业务，简单有do</p>
                                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                                'subject': '%s' % subject,
                                'email_to': '%s' % process.approver.work_email,
                                'auto_delete': False,
                                'email_from':self.get_mail_server_name(),
                            }).send()
                            self.message_post(body=process.approver_old.name+u'将审批权限授给'+process.approver.name)
                            process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                            self.add_follower(employee_id=process.approver.id)
                        self.write({'current_approver_user': [(4, process.approver.user_id.id)]})
                    for user in self.current_approver_user:
                        self.write({'his_app_user': [(4, user.id)]})
                    if process_03.is_pass or process_03.is_risk:
                        self.signal_workflow('btn_to_yfb')
                        self.write({'is_click_03':False})
                        if process_03.is_pass:
                            if process_03.reason:
                                self.message_post(body=process_03.approver.name+u'在待发布阶段二级审批意见:通过,原因：'+process_03.reason)
                            else:
                                self.message_post(body=process_03.approver.name+u'在待发布阶段二级审批意见:通过')
                        if process_03.is_risk:
                            if process_03.reason:
                                self.message_post(body=process_03.approver.name+u'在待发布阶段二级审批意见:带风险通过,原因：'+process_03.reason)
                            else:
                                self.message_post(body=process_03.approver.name+u'在待发布阶段二级审批意见:带风险通过')
                    elif process_03.is_refuse:
                        self.message_post(body=process_03.approver.name+u'在待发布阶段二级审批不同意，原因:'+process_03.reason)
                        # self.signal_workflow('dfb_to_draft')
                        self.write({'is_click_03':False})
                        proces_03all = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id),('ver_state','=',self.version_state)])
                        proces_03all.unlink()
                        self.write({'is_click_03':False,'is_finish_03':False})

    @api.model
    def wkf_zanting(self):
        self.write({'version_state': 'pause'})

    @api.model
    def wkf_zhongzhi(self):
        self.write({'version_state': 'stop'})

    reason_request = fields.Text(string="申请原因",track_visibility='onchange')
    agree = fields.Boolean(string="同意")

    @api.onchange("agree")
    def is_agree_change(self):
        for rec in self:
            if rec.agree:
                rec.disagree = False

    disagree = fields.Boolean(string="不同意")

    @api.onchange("disagree")
    def is_disagree_change(self):
        for rec in self:
            if rec.disagree:
                rec.agree = False

    comments = fields.Text(string="审批意见",track_visibility='onchange')

    is_zanting = fields.Boolean(string="标记是否申请暂停")
    is_zanting_back = fields.Boolean(string="标记是否申请恢复暂停")
    is_zhongzhi = fields.Boolean(string="标记是否申请中止")

    is_zantingtj = fields.Boolean(string="标记是否提交暂停")
    is_zanting_backtj = fields.Boolean(string="标记是否提交恢复暂停")
    is_zhongzhitj = fields.Boolean(string="标记是否提交中止")
    is_ztpage = fields.Boolean(string="标记页面是否显示")
    execption_id = fields.Many2one('dtdream_execption',string="待提交例外")
    execption_flag = fields.Boolean(string="标记是否存在未提交例外")

    @api.constrains('agree')
    def _com_agree(self):
        if self.is_zhongzhi and self.agree:
            if self.version_state=='initialization':
                self.version_state_old='initialization'
                self.signal_workflow('draft_to_vzhongzhi')
            if self.version_state=='Development':
                self.version_state_old='Development'
                self.signal_workflow('kaifa_to_vzhongzhi')
            if self.version_state=='pending':
                self.version_state_old='pending'
                self.signal_workflow('dfb_to_vzhongzhi')
            if self.version_state=='released':
                self.version_state_old='released'
                self.signal_workflow('yfb_to_vzhongzhi')
            if self.version_state=='pause':
                self.version_state_old='pause'
                self.signal_workflow('vzanting_to_vzhongzhi')
            self.write({'is_zhongzhi':False,'is_zhongzhitj':False})
        elif not self.is_zhongzhi and self.is_zanting and self.agree:
            if self.version_state=='initialization':
                self.version_state_old='initialization'
                self.signal_workflow('draft_to_vzanting')
            if self.version_state=='Development':
                self.version_state_old='Development'
                self.signal_workflow('kaifa_to_vzanting')
            if self.version_state=='pending':
                self.version_state_old='pending'
                self.signal_workflow('dfb_to_vzanting')
            if self.version_state=='released':
                self.version_state_old='released'
                self.signal_workflow('yfb_to_vzanting')
            self.write({'is_zanting':False,'is_zantingtj':False})
        if self.is_zanting_back and self.agree:
            if self.version_state_old=='initialization':
                self.signal_workflow('vzanting_to_draft')
            if self.version_state_old=='Development':
                self.signal_workflow('vzanting_to_kaifa')
            if self.version_state_old=='pending':
                self.signal_workflow('vzanting_to_dfb')
            if self.version_state_old=='released':
                self.signal_workflow('vzanting_to_yfb')
            self.write({'is_zanting_back':False,'is_zanting_backtj':False})

    #申请暂停
    @api.multi
    def do_zanting(self):
        if self.is_click_01 or self.is_click_02 or self.is_click_03:
            raise ValidationError("已提交审批，不能提交暂停")
        else:
            self.write({'reason_request':'','agree':False,'disagree':False,'comments':'','is_zanting':True,'is_ztpage':True})

    #暂停提交
    @api.multi
    def do_zantingtj(self):
        if self.reason_request:
            self.write({'is_zantingtj':True})
            self.current_approver_user = [(5,)]
            self.write({'current_approver_user': [(4,self.proName.department.manager_id.user_id.id)]})
            if not self.proName.department.manager_id:
                raise ValidationError(u"请配置%s的部门主管" %(self.proName.department.name))
            if self.proName.department_2:
                subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            else:
                subject=self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            appellation = self.proName.department.manager_id.name+u",您好"
            content = self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"的暂停申请，待您审批"
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
            url = base_url+link
            self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                             <p>%s</p>
                             <p> 请点击链接进入:
                             <a href="%s">%s</a></p>
                            <p>dodo</p>
                             <p>万千业务，简单有do</p>
                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                'subject': '%s' % subject,
                'email_to': '%s' % self.proName.department.manager_id.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()
        else:
            raise ValidationError('申请原因未填写')

     #暂停恢复

    #暂停恢复
    @api.multi
    def do_zanting_back(self):
         self.write({'reason_request':'','agree':False,'disagree':False,'comments':'','is_zanting_back':True})

    #恢复暂停提交
    @api.multi
    def do_zanting_backtj(self):
        if self.reason_request:
            self.write({'is_zanting_backtj':True})
            self.current_approver_user = [(5,)]
            if not self.proName.department.manager_id:
                raise ValidationError(u"请配置%s的部门主管" %(self.proName.department.name))
            if self.proName.department_2:
                subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            else:
                subject=self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            appellation = self.proName.department.manager_id.name+u",您好"
            content = self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"的中止申请，待您审批"
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
            url = base_url+link
            self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                             <p>%s</p>
                             <p> 请点击链接进入:
                             <a href="%s">%s</a></p>
                            <p>dodo</p>
                             <p>万千业务，简单有do</p>
                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                'subject': '%s' % subject,
                'email_to': '%s' % self.proName.department.manager_id.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()
            self.write({'current_approver_user': [(4,self.proName.department.manager_id.user_id.id)]})
        else:
            raise ValidationError('申请原因未填写')



    #中止恢复
    @api.multi
    def do_zhongzhi_back(self):
        if self.version_state_old=='initialization':
            self.signal_workflow('vzhongzhi_to_draft')
        if self.version_state_old=='Development':
            self.signal_workflow('vzhongzhi_to_kaifa')
        if self.version_state_old=='pending':
            self.signal_workflow('vzhongzhi_to_dfb')
        if self.version_state_old=='pause':
            self.signal_workflow('vzhongzhi_to_vzanting')
        if self.version_state_old=='released':
            self.signal_workflow('vzhongzhi_to_yfb')
        self.write({'reason_request':'','agree':False,'disagree':False,'comments':''})


    #申请中止
    @api.multi
    def do_zhongzhi(self):
        if self.is_click_01 or self.is_click_02 or self.is_click_03:
            raise ValidationError("已提交审批，不能提交中止")
        else:
            self.write({'reason_request':'','agree':False,'disagree':False,'comments':'','is_zhongzhi':True,'is_ztpage':True})

    #中止提交
    @api.multi
    def do_zhongzhitj(self):
        if self.reason_request:
            self.write({'is_zhongzhitj':True})
            self.current_approver_user = [(5,)]
            self.write({'current_approver_user': [(4,self.proName.department.manager_id.user_id.id)]})
            if not self.proName.department.manager_id:
                raise ValidationError(u"请配置%s的部门主管" %(self.proName.department.name))
            subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            appellation = self.proName.department.manager_id.name+u",您好"
            content = self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"的中止申请，待您审批"
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % self.id
            url = base_url+link
            self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                             <p>%s</p>
                             <p> 请点击链接进入:
                             <a href="%s">%s</a></p>
                            <p>dodo</p>
                             <p>万千业务，简单有do</p>
                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                'subject': '%s' % subject,
                'email_to': '%s' % self.proName.department.manager_id.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()
        else:
            raise ValidationError('申请原因未填写')

    def action_makeexception(self, cr, uid, ids, context=None):
        opportunity = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'dtdream_rd_prod', 'act_dtdream_exceptionedit', context)
        res['context'] = {
            'default_name': opportunity.execption_id.name.id,
            'default_version': opportunity.execption_id.version.id,
            'default_reason': opportunity.execption_id.reason,
            'default_approver_fir': opportunity.execption_id.approver_fir.id,
            'default_approver_sec': opportunity.execption_id.approver_sec.id,
            'default_mark':False
        }
        return res

    #提交例外
    @api.multi
    def execptiontj(self):
        if not self.approver_fir:
            raise ValidationError(u"第一审批人不能为空")
        if self.proName.department_2:
            subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
        else:
            subject=self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
        appellation = self.proName.department.manager_id.name+u",您好"
        content = self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"的例外申请，待您审批"
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream_execption' % self.execption_id.id
        url = base_url+link
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % self.approver_fir.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()
        self.execption_id.current_approver_user = [(5,)]
        self.execption_id.write({'state':'yjsp','current_approver_user':[(4,self.approver_fir.user_id.id)]})
        self.write({'execption_id':None,'execption_flag':False})


#版本审批基础数据配置
class dtdream_rd_approver_ver(models.Model):
    _name = 'dtdream_rd_approver_ver'
    name = fields.Many2one('dtdream_rd_config',string="角色")
    ver_state = fields.Selection([('initialization','计划中'),('Development','开发中'),('pending','待发布')],string='阶段')
    level = fields.Selection([('level_01','一级'),('level_02','二级')],string='级别')
    department = fields.Many2one('hr.department','部门')

    @api.onchange('ver_state')
    def get_is_pending(self):
        if self.ver_state=='pending':
            self.is_pending=True
        else:
            self.is_pending=False

    is_pending = fields.Boolean("是否待发布")

    @api.onchange('level')
    def _is_level(self):
        if self.level=='level_01':
            self.is_level=True
        else:
            self.is_level=False

    is_level = fields.Boolean( string="是否一级",readonly=True)

    # @api.model
    # def create(self, vals):
    #     if 'level'in vals and vals['level']=='level_02':
    #         if not vals['department']:
    #             raise ValidationError('请填写部门')
    #     result = super(dtdream_rd_approver_ver, self).create(vals)
    #     return  result


#版本审批意见
class dtdream_rd_process_ver(models.Model):
    _name = 'dtdream_rd_process_ver'
    ver_state = fields.Selection([('initialization','计划中'),('Development','开发中'),('pending','待发布')],string='阶段', readonly=True)
    role = fields.Many2one('dtdream_rd_config',string="角色",readonly=True)
    approver = fields.Many2one('hr.employee',string="审批人",help="可选择进行授权")
    level = fields.Selection([('level_01','一级'),('level_02','二级')],string='级别',readonly=True)
    approver_old = fields.Many2one('hr.employee',string="审批人")


    @api.onchange("is_pass")
    def is_pass_change(self):
        for rec in self:
            if rec.is_pass and rec.is_refuse or rec.is_pass and rec.is_risk:
                rec.is_refuse = False
                rec.is_risk = False

    @api.onchange("is_refuse")
    def is_refuse_change(self):
        for rec in self:
            if rec.is_pass and rec.is_refuse or rec.is_refuse and rec.is_risk:
                rec.is_risk = False
                rec.is_pass = False

    @api.onchange("is_risk")
    def is_risk_change(self):
        for rec in self:
            if rec.is_pass and rec.is_risk or rec.is_refuse and rec.is_risk:
                rec.is_refuse = False
                rec.is_pass = False

    is_pass = fields.Boolean("通过")
    is_refuse = fields.Boolean("不通过")
    is_risk = fields.Boolean("带风险通过")
    reason = fields.Text("意见")

    process_01_id = fields.Many2one('dtdream_rd_version',string='研发版本')
    process_02_id = fields.Many2one('dtdream_rd_version',string='研发版本')
    process_03_id = fields.Many2one('dtdream_rd_version',string='研发版本')

    is_new = fields.Boolean(string="标记是否为新",default=True)

    @api.model
    def _compute_editable(self):
        for rec in self:
            if rec.ver_state=='initialization':
                if rec.level=='level_01':
                    if rec.process_01_id.version_state==rec.ver_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new and not rec.process_01_id.is_finish_01:
                        rec.editable=True
                    else:
                        rec.editable=False
                if rec.level=='level_02':
                    if rec.process_01_id.version_state==rec.ver_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new:
                        rec.editable=True
                    else:
                        rec.editable=False
            if rec.ver_state=='Development':
                if rec.level=='level_01':
                    if rec.process_02_id.version_state==rec.ver_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new and not rec.process_02_id.is_finish_02:
                        rec.editable=True
                    else:
                        rec.editable=False
                if rec.level=='level_02':
                    if rec.process_02_id.version_state==rec.ver_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new:
                        rec.editable=True
                    else:
                        rec.editable=False
            if rec.ver_state=='pending':
                if rec.level=='level_01':
                    if rec.process_03_id.version_state==rec.ver_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new and not rec.process_03_id.is_finish_03:
                        rec.editable=True
                    else:
                        rec.editable=False
                if rec.level=='level_02':
                    if rec.process_03_id.version_state==rec.ver_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new:
                        rec.editable=True
                    else:
                        rec.editable=False

    editable = fields.Boolean(string="能否修改",compute = _compute_editable,default=True)

    @api.model
    def _compute_is_Qa(self):
        users =  self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users
        ids = []
        for user in users:
            ids+=[user.id]
            for rec in self:
                if self.env.user.id in ids:
                    rec.is_Qa = True
                else:
                    rec.is_Qa=False
    is_Qa = fields.Boolean(string="是否在QA组",compute=_compute_is_Qa,readonly=True)
