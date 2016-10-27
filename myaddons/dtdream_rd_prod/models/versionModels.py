#-*- coding: UTF-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
import openerp
from openerp.osv import expression
from datetime import datetime

#版本
class dtdream_rd_version(models.Model):
    _name = 'dtdream_rd_version'
    _inherit =['mail.thread']
    _description = u"产品版本"
    _rec_name = 'version_numb'
    version_numb = fields.Char("版本号",required=True,track_visibility='onchange')
    @api.onchange('proName')
    def _get_pro(self):
        self.name = self.proName.name

    name=fields.Char(string="产品名称")
    proName = fields.Many2one("dtdream_prod_appr" ,required=True)


    pro_flag = fields.Selection([('flag_06','正式版本'),('flag_01','内部测试版本'),('flag_02','外部测试版本'),('flag_03','公测版本'),
                                ('flag_04','演示版本'),('flag_05','补丁版本')],
                             '版本标识',track_visibility='onchange',required=True)
    version_state = fields.Selection([
        ('draft','草稿'),
        ('initialization','计划中'),
        ('Development','开发中'),
        ('pending','待发布'),
        ('pause','暂停'),
        ('stop','中止'),
        ('released','已发布')],
        '版本状态',default="draft")

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
    plan_pub_time = fields.Date("计划发布完成时间",track_visibility='onchange',required=True)
    plan_mater=fields.Text("版本计划材料",track_visibility='onchange')

    actual_dev_time = fields.Date("实际开发开始时间",help="版本开始时间指迭代开发开始时间",track_visibility='onchange')
    dev_mater = fields.Text("版本开发材料",track_visibility='onchange')

    actual_check_pub_time =fields.Date("实际验证发布开始时间",track_visibility='onchange')
    actual_pub_time = fields.Date("实际发布完成时间",track_visibility='onchange')
    place = fields.Char('版本存放位置',track_visibility='onchange')
    Material =fields.Text('版本发布材料',track_visibility='onchange')

    acceptance_results = fields.Selection([
        ('A','A'),
        ('B','B'),
        ('C','C'),
        ('D','D')],
        string="验收结果"
    )

    ys_jy = fields.Char(string="验收发现紧要问题数")
    ys_yz = fields.Char(string="验收发现严重问题数")
    ys_yb = fields.Char(string="验收发现一般问题数")
    ys_ts = fields.Char(string="验收发现提示问题数")
    yl_jy = fields.Char(string="遗留紧要问题数")
    yl_yz = fields.Char(string="遗留严重问题数")
    yl_yb = fields.Char(string="遗留一般问题数")
    yl_ts = fields.Char(string="遗留提示问题数")

    replanning_ids= fields.One2many('dtdream.rd.replanning','version',string="重计划",domain=[('state','=','state_03')])

    cg_finsh_time = fields.Datetime(string="草稿阶段完成时间")
    jhz_finsh_time = fields.Datetime(string="计划中阶段完成时间")
    kfz_finsh_time = fields.Datetime(string="开发中阶段完成时间")
    dfb_finsh_time = fields.Datetime(string="待发布阶段完成时间")

    @api.multi
    def _compute_proName(self):
        for rec in self:
            rec.PDT = rec.proName.PDT.id
    PDT = fields.Many2one("hr.employee",string="PDT经理",compute=_compute_proName)

    @api.constrains('department')
    def _onchang_dep(self):
        if self.department!=self.proName.department:
            raise ValidationError(u"版本与产品的部门不同")

    @api.constrains('department_2')
    def _onchang_dep_2(self):
        if self.department_2 != self.proName.department_2:
            raise ValidationError(u"版本与产品的二级部门不同")

    department = fields.Many2one('hr.department',string='部门')
    department_2 = fields.Many2one('hr.department',string='二级部门')

    #部门的联动
    @api.onchange('department_2')
    def _chang_department(self):
        if self.department_2:
            self.department = self.department_2.parent_id

    @api.onchange('department')
    def _chang_department_2(self):
        domain = {}
        try:
            rd_list= openerp.tools.config['rd_list'].split(',')
        except Exception,e:
            rd_list=[]

        if self.department:
            domain['department_2'] = [('parent_id', '=', self.department.id)]
        else:
            if len(rd_list) != 0:
                domain['department_2'] = [('parent_id.parent_id', '=', False),'|','|',('parent_id.name', '=', rd_list[0]),('parent_id.name', '=', rd_list[1]),('parent_id.name', '=', rd_list[2])]
                domain['department'] = [('parent_id', '=', False),'|','|',('name', '=', rd_list[0]),('name', '=', rd_list[1]),('name', '=', rd_list[2])]
        return {'domain': domain}

    @api.one
    def _compute_create(self):
        role = self.env["dtdream_rd_config"].search([("name", "=", u"PDT经理")])
        pdt = False
        for rec in self.proName.role_ids:
            if role ==rec.cof_id:
                if rec.person:
                    if rec.person.user_id == self.env.user:
                        pdt =True
                        break
        if self.create_uid==self.env.user or pdt:
            self.is_create=True
        else:
            self.is_create=False
    is_create = fields.Boolean(string="是否创建者",compute=_compute_create,store=True,default=True)

    @api.one
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

    @api.one
    def _compute_is_shenpiren(self):
        if self.env.user in self.current_approver_user:
            self.is_shenpiren=True
        else:
            self.is_shenpiren = False
    is_shenpiren = fields.Boolean(string="是否审批人",compute=_compute_is_shenpiren,readonly=True)

    @api.one
    def _compute_liwai_log(self):
        cr = self.env["dtdream_execption"].search([("name.id", "=", self.proName.id),('version.id','=',self.id)])
        self.liwai_nums = len(cr)

    liwai_nums = fields.Integer(compute='_compute_liwai_log', string="例外记录",store=True)

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

    @api.multi
    def _wkf_message_post(self,statechange):
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">版本号</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.proName.name,self.version_numb,statechange))

    @api.model
    def wkf_draft(self):
        if self.version_state=='initialization':
            self.write({'is_click_01':False,'is_finish_01':False})
            processes01 = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',self.id)])
            processes01.unlink()
            self._wkf_message_post(statechange=u'版本状态: 计划中->草稿')
        elif self.version_state=='pause':
            self._wkf_message_post(statechange=u'版本状态: 暂停->草稿')
        elif self.version_state=='stop':
            self._wkf_message_post(statechange=u'版本状态: 中止->草稿')
        self.write({'version_state': 'draft'})


    @api.model
    def wkf_jihuazhong(self):
        if self.version_state=='Development':
            self.write({'is_click_01':False,'is_click_02':False,'is_finish_01':False,'is_finish_02':False})
            processes01 = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',self.id)])
            processes01.unlink()
            processes02 = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',self.id)])
            processes02.unlink()
            self._wkf_message_post(statechange=u'版本状态: 开发中->计划中')
        elif self.version_state=='pause':
            self._wkf_message_post(statechange=u'版本状态: 暂停->计划中')
        elif self.version_state=='stop':
            self._wkf_message_post(statechange=u'版本状态: 中止->计划中')
        elif self.version_state=='draft':
            self._wkf_message_post(statechange=u'版本状态: 草稿->计划中')
            self.write({'cg_finsh_time':datetime.now()})
        self.write({'version_state': 'initialization'})

    @api.model
    def wkf_kaifa(self):
        if self.version_state=='pending':
            self.write({'is_click_02':False,'is_click_03':False,'is_finish_02':False,'is_finish_03':False})
            processes02 = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',self.id)])
            processes02.unlink()
            processes03 = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id)])
            processes03.unlink()
            self._wkf_message_post(statechange=u'版本状态: 待发布->开发中')
        elif self.version_state=='pause':
            self._wkf_message_post(statechange=u'版本状态: 暂停->开发中')
        elif self.version_state=='stop':
            self._wkf_message_post(statechange=u'版本状态: 中止->开发中')
        elif self.version_state=='initialization':
            self._wkf_message_post(statechange=u'版本状态: 计划中->开发中')
            self.write({'jhz_finsh_time':datetime.now()})
        self.write({'version_state': 'Development'})

    @api.model
    def wkf_dfb(self):
        if self.version_state=='released':
            self.write({'is_click_03':False,'is_finish_03':False})
            processes03 = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id)])
            processes03.unlink()
            self._wkf_message_post(statechange=u'版本状态: 已发布->待发布')
        elif self.version_state=='pause':
            self._wkf_message_post(statechange=u'版本状态: 暂停->待发布')
        elif self.version_state=='stop':
            self._wkf_message_post(statechange=u'版本状态: 中止->待发布')
        elif self.version_state=='Development':
            self._wkf_message_post(statechange=u'版本状态: 开发中->待发布')
            self.write({'kfz_finsh_time':datetime.now()})
        self.write({'version_state': 'pending'})

    @api.model
    def wkf_yfb(self):
        if self.version_state=='pause':
            self._wkf_message_post(statechange=u'版本状态: 暂停->已发布')
        elif self.version_state=='stop':
            self._wkf_message_post(statechange=u'版本状态: 中止->已发布')
        elif self.version_state=='pending':
            self._wkf_message_post(statechange=u'版本状态: 待发布->已发布')
            self.write({'dfb_finsh_time':datetime.now()})
        self.write({'version_state': 'released'})
        self.current_approver_user = [(5,)]

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

    @api.onchange('message_follower_ids')
    def _compute_follower(self):
        self.followers_user = False
        for foll in self.message_follower_ids:
            self.write({'followers_user': [(4,foll.partner_id.user_ids.id)]})
            if foll.partner_id.user_ids not in self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users:
                self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").sudo().write({'users': [(4,foll.partner_id.user_ids.id)]})

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
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

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
                self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><th style="padding:10px">版本</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作人</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.proName.name,self.version_numb,process.approver_old.name,u'将审批权限授给'+process.approver.name))
                process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                self.add_follower(employee_id=process.approver.id)
                self.write({'current_approver_user': [(4,process.approver.user_id.id)]})

    @api.constrains('process_02_ids')
    def con_pro_02_ids(self):
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
                self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><th style="padding:10px">版本</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作人</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.proName.name,self.version_numb,process.approver_old.name,u'将审批权限授给'+process.approver.name))
                process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                self.add_follower(employee_id=process.approver.id)
                self.write({'current_approver_user': [(4,process.approver.user_id.id)]})

    @api.constrains('process_03_ids')
    def con_pro_03_ids(self):
        # processes = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',self.id),('ver_state','=',self.version_state),('level','=','level_01'),('is_new','=',True)])
        for process in self.process_03_ids:
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
                self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><th style="padding:10px">版本</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作人</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.proName.name,self.version_numb,process.approver_old.name,u'将审批权限授给'+process.approver.name))
                process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                self.add_follower(employee_id=process.approver.id)
                self.write({'current_approver_user': [(4,process.approver.user_id.id)]})

    @api.model
    def wkf_zanting(self):
        if self.version_state=='draft':
            self._wkf_message_post(statechange=u'版本状态: 草稿->暂停')
        elif self.version_state=='initialization':
            self._wkf_message_post(statechange=u'版本状态: 计划中->暂停')
        elif self.version_state=='Development':
            self._wkf_message_post(statechange=u'版本状态: 开发中->暂停')
        elif self.version_state=='pending':
            self._wkf_message_post(statechange=u'版本状态: 待发布->暂停')
        elif self.version_state=='stop':
            self._wkf_message_post(statechange=u'版本状态: 中止->暂停')
        elif self.version_state=='released':
            self._wkf_message_post(statechange=u'版本状态: 已发布->暂停')
        self.write({'version_state': 'pause'})

    @api.model
    def wkf_zhongzhi(self):
        if self.version_state=='draft':
            self._wkf_message_post(statechange=u'版本状态: 草稿->中止')
        elif self.version_state=='initialization':
            self._wkf_message_post(statechange=u'版本状态: 计划中->中止')
        elif self.version_state=='Development':
            self._wkf_message_post(statechange=u'版本状态: 开发中->中止')
        elif self.version_state=='pending':
            self._wkf_message_post(statechange=u'版本状态: 待发布->中止')
        elif self.version_state=='pause':
            self._wkf_message_post(statechange=u'版本状态: 暂停->中止')
        elif self.version_state=='released':
            self._wkf_message_post(statechange=u'版本状态: 已发布->中止')
        self.write({'version_state': 'stop'})

    reason_request = fields.Text(string="申请原因")
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

    comments = fields.Text(string="审批意见")

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
        if self.comments and self.agree:
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><th style="padding:10px">版本</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">审批人</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name,self.version_numb,self.department.manager_id.name,u'审批意见:同意,意见：'+self.comments))
            

    @api.constrains('disagree')
    def _com_disagree(self):
        if self.is_zhongzhitj and self.disagree:
            if not self.comments:
                raise ValidationError(u'不同意时意见必填')
            self.write({'is_zhongzhitj':False})
        elif not self.is_zhongzhitj and self.is_zantingtj and self.disagree:
            if not self.comments:
                raise ValidationError(u'不同意时意见必填')
            self.write({'is_zantingtj':False})
        if self.is_zanting_backtj and self.disagree:
            if not self.comments:
                raise ValidationError(u'不同意时意见必填')
            self.write({'is_zanting_backtj':False})
        if self.comments and self.disagree:
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><th style="padding:10px">版本</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">审批人</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.proName.name,self.version_numb,self.proName.department.manager_id.name,u'审批意见:不同意,意见：'+self.comments))
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
        if self.disagree:
            self.write({'disagree':'','comments':''})
        if self.reason_request:
            is_plccb = False
            plccb=None
            for role in self.proName.role_ids:
                if role.cof_id.name=="PL-CCB":
                    is_plccb=True
                    plccb=role.person
                    break
            if not is_plccb or not plccb:
                raise ValidationError(u"该产品没有配置PL-CCB")
            self.write({'is_zantingtj':True})
            self.current_approver_user = [(5,)]
            # if not self.proName.department.manager_id:
            #     raise ValidationError(u"请配置%s的部门主管" %(self.proName.department.name))
            self.write({'current_approver_user': [(4,plccb.user_id.id)]})
            # self.add_follower(employee_id=self.proName.department.manager_id.id)
            if self.proName.department_2:
                subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            else:
                subject=self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            appellation = plccb.name+u",您好"
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
                'email_to': '%s' % plccb.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.proName.name,self.version_numb,u'提交暂停',self.reason_request))
        else:
            raise ValidationError('申请原因未填写')



    #暂停恢复
    @api.multi
    def do_zanting_back(self):
         self.write({'reason_request':'','agree':False,'disagree':False,'comments':'','is_zanting_back':True})

    #恢复暂停提交
    @api.multi
    def do_zanting_backtj(self):
        if self.disagree:
            self.write({'disagree':'','comments':''})
        if self.reason_request:
            is_plccb = False
            plccb=None
            for role in self.proName.role_ids:
                if role.cof_id.name=="PL-CCB":
                    is_plccb=True
                    plccb=role.person
                    break
            if not is_plccb or not plccb:
                raise ValidationError(u"该产品没有配置PL-CCB")
            self.write({'is_zanting_backtj':True})
            self.current_approver_user = [(5,)]
            # if not self.proName.department.manager_id:
            #     raise ValidationError(u"请配置%s的部门主管" %(self.proName.department.name))
            if self.proName.department_2:
                subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            else:
                subject=self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            appellation = plccb.name+u",您好"
            content = self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"的恢复暂停申请，待您审批"
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
                'email_to': '%s' % plccb.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()
            self.write({'current_approver_user': [(4,plccb.user_id.id)]})
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.proName.name,self.version_numb,u'恢复暂停',self.reason_request))
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
        if self.disagree:
            self.write({'disagree':'','comments':''})
        if self.reason_request:
            is_plccb = False
            plccb=None
            for role in self.proName.role_ids:
                if role.cof_id.name=="PL-CCB":
                    is_plccb=True
                    plccb=role.person
                    break
            if not is_plccb or not plccb:
                raise ValidationError(u"该产品没有配置PL-CCB")
            self.write({'is_zhongzhitj':True})
            self.current_approver_user = [(5,)]
            # if not self.proName.department.manager_id:
            #     raise ValidationError(u"请配置%s的部门主管" %(self.proName.department.name))
            self.write({'current_approver_user': [(4,plccb.user_id.id)]})
            # self.add_follower(employee_id=self.proName.department.manager_id.id)
            if self.proName.department_2:
                subject=self.proName.department.name+u"/"+self.proName.department_2.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            else:
                subject=self.proName.department.name+u"的"+self.proName.name+u"的"+self.version_numb+u"待您审批"
            appellation = plccb.name+u",您好"
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
                'email_to': '%s' % plccb.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.proName.name,self.version_numb,u'提交中止',self.reason_request))
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

    @api.model
    def read_group(self,domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
            if menu == u"我相关的":
                uid = self._context.get('uid', '')
                em = self.env['hr.employee'].search([('user_id','=',self.env.uid)])
                domain = expression.AND([['|','|','|','|','|',('department','=',em.department_id.id),('create_uid','=',uid),('current_approver_user','=',uid),('his_app_user','=',uid),('followers_user','=',uid),('department_2','=',em.department_id.id)], domain])
        res = super(dtdream_rd_version, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
            if menu == u"我相关的":
                uid = self._context.get('uid', '')
                em = self.env['hr.employee'].search([('user_id','=',self.env.uid)])
                domain = expression.AND([['|','|','|','|','|',('department','=',em.department_id.id),('create_uid','=',uid),('current_approver_user','=',uid),('his_app_user','=',uid),('followers_user','=',uid),('department_2','=',em.department_id.id)], domain])
        return super(dtdream_rd_version, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)



    def process_email_send(self,version,process,state):
        subject=u'请尽快处理'+version.proName.name+u'产品'+version.version_numb+u'版本'+state+u'状态审批！'
        appellation = process.approver.name+u",您好"
        content = version.proName.name+u'产品'+version.version_numb+u'版本'+state+u'状态的审批您还未处理，请及时处理！'
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % version.id
        url = base_url+link
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,version.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % process.approver.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()

    def special_send_email(self,version,state):
        subject=u'请尽快处理'+version.proName.name+u'产品'+version.version_numb+u'版本申请'+state+u'审批！'
        appellation = version.proName.department.maneger_id.name+u",您好"
        content = version.proName.name+u'产品'+version.version_numb+u'版本申请'+state+u'的审批您还未处理，请及时处理！'
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % version.id
        url = base_url+link
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,version.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % version.proName.department.maneger_id.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()



    #定时发送邮件提醒
    @api.model
    def timing_send_email(self):
        versions=self.env['dtdream_rd_version'].sudo().search([('version_state','not in',('draft','stop','released'))])
        for version in versions:
            if version.version_state=="initialization":
                if version.is_click_01:
                    for process in version.process_01_ids:
                        if ( not process.is_pass and not process.is_risk):
                            self.process_email_send(version=version,process=process,state=u'计划中')
                elif version.is_zhongzhitj:
                    self.special_send_email(version=version,state=u"中止")
                elif version.is_zantingtj and not version.is_zhongzhitj:
                     self.special_send_email(version=version,state=u"暂停")
            elif version.version_state=="Development":
                if version.is_click_02:
                    for process in version.process_02_ids:
                        if ( not process.is_pass and not process.is_risk):
                            self.process_email_send(version=version,process=process,state=u'开发中')
                elif version.is_zhongzhitj:
                    self.special_send_email(version=version,state=u"中止")
                elif version.is_zantingtj and not version.is_zhongzhitj:
                     self.special_send_email(version=version,state=u"暂停")
            elif version.version_state=="pending":
                if version.is_click_03:
                    for process in version.process_03_ids:
                        if ( not process.is_pass and not process.is_risk):
                            self.process_email_send(version=version,process=process,state=u'待发布')
                elif version.is_zhongzhitj:
                    self.special_send_email(version=version,state=u"中止")
                elif version.is_zantingtj and not version.is_zhongzhitj:
                     self.special_send_email(version=version,state=u"暂停")
            elif version.version_state=="pause":
                if version.is_zhongzhitj:
                    self.special_send_email(version=version,state=u"中止")
                elif version.is_zanting_backtj:
                     self.special_send_email(version=version,state=u"恢复暂停")


#版本审批基础数据配置
class dtdream_rd_approver_ver(models.Model):
    _name = 'dtdream_rd_approver_ver'
    name = fields.Many2one('dtdream_rd_config',string="角色")
    ver_state = fields.Selection([('initialization','计划中'),('Development','开发中'),('pending','待发布')],string='阶段')
    level = fields.Selection([('level_01','一级'),('level_02','二级')],string='级别')
    department = fields.Many2one('hr.department','部门')
    is_formal = fields.Boolean(string="是否为正式版本")

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

    @api.one
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
