# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError

class dtdream_rd_prod(models.Model):
    _name = 'dtdream_rd_prod'
    name = fields.Char("项目名称")
    code = fields.Char("项目编码")


#研发产品
class dtdream_prod_appr(models.Model):
    _name = 'dtdream_prod_appr'
    _inherit = ['mail.thread']
    department = fields.Many2one('hr.department','部门',track_visibility='onchange',required=True)
    department_2 = fields.Many2one('hr.department','二级部门',track_visibility='onchange',required=True)
    name=fields.Char('产品名称',required=True,track_visibility='onchange')

    state = fields.Selection([('state_00','草稿'),('state_01','立项'),('state_02','总体设计'),('state_03','迭代开发'),('state_04','验证发布'),('state_05','完成')],'产品状态',track_visibility='onchange',readonly=True,default='state_00')

    version_ids = fields.One2many('dtdream_rd_version','proName','版本')
    role_ids = fields.One2many('dtdream_rd_role','role_id',string='角色')

    pro_time = fields.Date('立项时间',track_visibility='onchange')
    overall_plan_time = fields.Date('总体设计计划完成时间',track_visibility='onchange')
    overall_actual_time = fields.Date('总体设计实际完成时间',track_visibility='onchange')

    start_pro_mar = fields.Text('立项材料',track_visibility='onchange')
    overall_mar = fields.Text('总体设计材料',track_visibility='onchange')


    color = fields.Integer('Color Index')
    active = fields.Boolean(default=True)

    process_ids = fields.One2many('dtdream_rd_process','process_id',string="立项审批意见",track_visibility='onchange')

    ztsj_process_ids = fields.One2many('dtdream_rd_process','ztsj_process_id',string="总体设计审批意见",track_visibility='onchange')

    def add_follower(self, cr, uid, ids, employee_id, context=None):
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        if employee and employee.user_id:
            self.message_subscribe_users(cr, uid, ids, user_ids=[employee.user_id.id], context=context)
    
    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True, mail_create_nosubscribe=True)
        prod_id = super(dtdream_prod_appr, self).create(cr, uid, values, context=context)
        self.message_subscribe_users(cr, uid, [prod_id], user_ids=[uid], context=context)
        rold_ids = values['role_ids']
        for rold in rold_ids:
            if rold[2]['person']:
                self.add_follower(cr, uid, [prod_id], rold[2]['person'], context=context)
        return prod_id

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    @api.constrains('process_ids')
    def _compute_process_ids(self):
        for process in self.process_ids:
            if process.approver_old and process.approver!=process.approver_old:
                subject=process.approver.name+u"把"+self.department_2+u"的"+self.name+u"审批权限授予你"
                appellation = process.approver_old.name+u",您好"
                content = process.approver.name+u"把"+self.department_2+u"的"+self.name+u"审批权限授予你"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % self.id
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
                    'email_to': '%s' % process.approver_old.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()
        if self.state=='state_01':
            processes = self.env['dtdream_rd_process'].search([('process_id','=',self.id),('pro_state','=','state_01'),('level','=','level_01')])
            self.is_finsished_01 = True
            for process in processes:
                if not (process.is_pass or process.is_risk):
                    self.is_finsished_01 = False
                    break
            if self.is_finsished_01:
                for user in self.current_approver_user:
                    self.write({'his_app_user': [(4, user.id)]})
                processes = self.env['dtdream_rd_process'].search([('process_id','=',self.id),('pro_state','=','state_01'),('level','=','level_02'),('is_new','=',True)])
                if len(processes)==0:
                    ctd = self.env['dtdream_rd_approver'].search([('department','=',self.department.id)],limit=1)
                    self.env['dtdream_rd_process'].create({"role":ctd.name.id,"process_id":self.id,'pro_state':self.state,'approver':self.department.manager_id.id,'approver_old':self.department.manager_id.id,'level':'level_02'})       #审批意见记录创建
                    self.current_approver_user = [(5,)]
                    self.write({'current_approver_user': [(4,self.department.manager_id.user_id.id)]})
                else:
                    for user in self.current_approver_user:
                        self.write({'his_app_user': [(4, user.id)]})
                    self.current_approver_user = [(5,)]
                    if processes.is_pass or processes.is_risk:
                        self.signal_workflow('btn_to_ztsj')
                    else:
                        self.write({'is_appred':False})
                        self.signal_workflow('lixiang_to_draft')
                        self.write({'is_finsished_01':False})
                        processes = self.env['dtdream_rd_process'].search([('process_id','=',self.id)])
                        for process in processes:
                            process.write({'is_new':False})

    @api.constrains('ztsj_process_ids')
    def _compute_ztsj_process_ids(self):
        for process in self.ztsj_process_ids:
            if process.approver_old and process.approver!=process.approver_old:
                subject=process.approver.name+u"把"+self.department_2+u"的"+self.name+u"审批权限授予你"
                appellation = process.approver_old.name+u",您好"
                content = process.approver.name+u"把"+self.department_2+u"的"+self.name+u"审批权限授予你"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % self.id
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
                    'email_to': '%s' % process.approver_old.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()
        if self.state=='state_02' and self.is_appred:
            processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',self.id),('pro_state','=','state_02'),('level','=','level_01'),('is_new','=',True)])
            self.is_finsished_02 = True
            for process in processes:
                if not (process.is_pass or process.is_risk):
                    self.is_finsished_02 = False
                    break
            if self.is_finsished_02:
                for user in self.current_approver_user:
                    self.write({'his_app_user': [(4, user.id)]})
                processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',self.id),('pro_state','=','state_02'),('level','=','level_02'),('is_new','=',True)])
                if len(processes)==0:
                    ctd = self.env['dtdream_rd_approver'].search([('department','=',self.department.id)],limit=1)
                    self.env['dtdream_rd_process'].create({"role":ctd.name.id,"ztsj_process_id":self.id,'pro_state':self.state,'approver':self.department.manager_id.id,'approver_old':self.department.manager_id.id,'level':'level_02'})       #审批意见记录创建
                    self.current_approver_user = [(5,)]
                    self.write({'current_approver_user': [(4, self.department.manager_id.user_id.id)]})
                else:
                    for user in self.current_approver_user:
                        self.write({'his_app_user': [(4, user.id)]})
                    self.current_approver_user = [(5,)]
                    if processes.is_pass or processes.is_risk:
                        self.signal_workflow('btn_to_ddkf')
                    else:
                        self.write({'is_appred':False})
                        self.signal_workflow('ztsj_to_draft')
                        self.write({'is_finsished_01':False,'is_finsished_02':False})
                        processes = self.env['dtdream_rd_process'].search([('process_id','=',self.id)])
                        for process in processes:
                            process.write({'is_new':False})
                        ztsj_processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',self.id)])
                        for process in ztsj_processes:
                            process.write({'is_new':False})

    is_finsished_01 = fields.Boolean(string="立项多人审批是否结束",stroe=True)
    is_finsished_02 = fields.Boolean(string="总体设计多人审批是否结束",stroe=True)

    current_approver_user = fields.Many2many("res.users", "c_a_u_u",string="当前审批人用户")

    his_app_user = fields.Many2many("res.users" ,"h_a_u_u",string="历史审批人用户")

    @api.constrains('message_follower_ids')
    def _compute_follower(self):
        self.followers_user = False
        for foll in self.message_follower_ids:
            self.write({'followers_user': [(4,foll.partner_id.user_ids.id)]})

    followers_user = fields.Many2many("res.users" ,"f_u_u",string="关注者")
    is_appred = fields.Boolean(string="标识总体设计阶段提交按钮",default=False)

    @api.multi
    def message_unsubscribe(self, partner_ids=None, channel_ids=None,):
        if not partner_ids and not channel_ids:
            return True
        user_pid = self.env.user.partner_id.id
        if not channel_ids and set(partner_ids) == set([user_pid]):
            self.check_access_rights('read')
            self.check_access_rule('read')
        else:
            self.check_access_rights('write')
            self.check_access_rule('write')
        self.env['mail.followers'].sudo().search([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
            '|',
            ('partner_id', 'in', partner_ids or []),
            ('channel_id', 'in', channel_ids or [])
        ]).unlink()
        self._compute_follower()

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
        if self.env.user in users:
            self.is_Qa = True
        else:
            self.is_Qa=False
    is_Qa = fields.Boolean(string="是否在QA组",compute=_compute_is_Qa,readonly=True)

#部门的联动
    @api.onchange('department_2')
    def _chang_department(self):
        if self.department_2:
            self.department = self.department_2.parent_id

    @api.onchange('department')
    def _chang_department_2(self):
        domain = {}
        if self.department:
            if self.department.child_ids:
                self.department_2 =  self.department.child_ids[0]
                domain['department_2'] = [('parent_id', '=', self.department.id)]
        else:
            domain['department_2'] = [('parent_id.parent_id', '=', False)]
        return {'domain': domain}

    @api.model
    def wkf_draft(self):
        if self.state=='state_01':
            self.write({'is_appred':False})
            self.write({'is_finsished_01':False})
            processes = self.env['dtdream_rd_process'].search([('process_id','=',self.id)])
            # for process in processes:
            #     process.write({'is_new':False})
            processes.unlink()
        self.write({'state': 'state_00'})
        self.current_approver_user = [(5,)]


    @api.multi
    def wkf_lixiang(self):
        print self.message_follower_ids[0]
        self.message_follower_ids
        lg = len(self.version_ids)
        if self.state=="state_02":
            self.write({'is_appred':False})
            self.write({'is_finsished_01':False,'is_finsished_02':False})
            processes = self.env['dtdream_rd_process'].search([('process_id','=',self.id)])
            # for process in processes:
            #     process.write({'is_new':False})
            processes.unlink()
            ztsj_processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',self.id)])
            # for process in ztsj_processes:
            #     process.write({'is_new':False})
            ztsj_processes.unlink()
        if lg<=0:
            raise ValidationError("提交项目时必须至少有一个版本")
        self.write({'state': 'state_01'})
        records = self.env['dtdream_rd_approver'].search([('pro_state','=',self.state),('level','=','level_01')])           #审批人配置
        rold_ids = []
        for record in records:
            rold_ids +=[record.name.id]
        appro = self.env['dtdream_rd_role'].search([('role_id','=',self.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
        self.current_approver_user = [(5,)]
        for record in appro:
            self.env['dtdream_rd_process'].create({"role":record.cof_id.id, "process_id":self.id,'pro_state':self.state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_01'})       #审批意见记录创建
            self.write({'current_approver_user': [(4, record.person.user_id.id)]})
        processes = self.env['dtdream_rd_process'].search([('process_id','=',self.id),('pro_state','=','state_01'),('level','=','level_01'),('is_new','=',True)])
        if len(processes)==0:
            ctd = self.env['dtdream_rd_approver'].search([('department','=',self.department.id)],limit=1)
            self.env['dtdream_rd_process'].create({"role":ctd.name.id,"process_id":self.id,'pro_state':self.state,'approver':self.department.manager_id.id,'approver_old':self.department.manager_id.id,'level':'level_02'})       #审批意见记录创建
            self.current_approver_user = [(5,)]
            self.write({'current_approver_user': [(4, self.department.manager_id.user_id.id)]})


    @api.multi
    def wkf_ztsj(self):
        if self.state=="state_03":
            self.write({'is_appred':False})
            self.write({'is_finsished_02':False})
            ztsj_processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',self.id)])
            # for process in ztsj_processes:
            #     process.write({'is_new':False})
            ztsj_processes.unlink()
        self.write({'state': 'state_02'})

    @api.multi
    def wkf_ddkf(self):
        self.write({'state': 'state_03'})

    @api.multi

    def wkf_yzfb(self):
        self.write({'state': 'state_04'})

    @api.multi
    def wkf_jieshu(self):
        self.write({'state': 'state_05'})

    @api.multi
    def do_back(self):
        if self.state=="state_01":
            self.signal_workflow('lixiang_to_draft')
        if self.state=="state_02":
            self.signal_workflow('ztsj_to_lixiang')
        if self.state=="state_03":
            self.signal_workflow('ddkf_to_ztsj')
        if self.state=="state_04":
            self.signal_workflow('yzfb_to_ddkf')
        if self.state=="state_05":
            self.signal_workflow('js_to_yzfb')

class dtdream_rd_version(models.Model):
    _name = 'dtdream_rd_version'
    version_numb = fields.Char("版本号",required=True)
    @api.onchange('proName')
    def _get_pro(self):
        self.name = self.proName.name

    name=fields.Char()
    proName = fields.Many2one("dtdream_prod_appr" ,string='产品名称',required=True)


    pro_flag = fields.Selection([('flag_06','正式版本'),('flag_01','内部测试版本'),('flag_02','外部测试版本'),('flag_03','公测版本'),
                                ('flag_04','演示版本'),('flag_05','补丁版本')],
                             '版本标识')
    version_state = fields.Selection([
        ('initialization','草稿'),
        ('Development','开发中'),
        ('pending','待发布'),
        ('released','已发布')],
        '版本状态',default="initialization")
    plan_dev_time = fields.Date("计划开发开始时间",help="版本开始时间指迭代开发开始时间")
    plan_check_pub_time = fields.Date("计划开发完成时间")
    plan_pub_time = fields.Date("计划发布完成时间")
    plan_mater=fields.Text("版本计划材料")

    actual_dev_time = fields.Date("实际开发开始时间",help="版本开始时间指迭代开发开始时间")
    dev_mater = fields.Text("版本开发材料")

    actual_check_pub_time =fields.Date("实际验证发布开始时间")
    actual_pub_time = fields.Date("实际发布完成时间")
    place = fields.Char('版本存放位置')
    Material =fields.Text('版本发布材料')

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
    def wkf_draft(self):
        self.write({'version_state': 'initialization'})

    @api.model
    def wkf_kaifa(self):
        self.write({'version_state': 'Development'})

    @api.model
    def wkf_dfb(self):
        self.write({'version_state': 'pending'})

    @api.model
    def wkf_yfb(self):
        self.write({'version_state': 'released'})


#角色基础配置
class dtdream_rd_config(models.Model):
    _name = 'dtdream_rd_config'
    name = fields.Char('角色名称')
    cof_ids = fields.One2many('dtdream_rd_role','cof_id')
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


#产品里的人员
class dtdream_rd_role(models.Model):
    _name = 'dtdream_rd_role'
    role_id = fields.Many2one("dtdream_prod_appr")
    cof_id = fields.Many2one('dtdream_rd_config',string="角色")
    person = fields.Many2one("hr.employee",'人员')
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


#审批基础数据配置
class dtdream_rd_approver(models.Model):
    _name = 'dtdream_rd_approver'
    name = fields.Many2one('dtdream_rd_config',string="角色")
    pro_state = fields.Selection([('state_01','立项'),('state_02','总体设计')],string='阶段')
    level = fields.Selection([('level_01','一级'),('level_02','二级')],string='级别')

    @api.onchange('level')
    def _is_level(self):
        if self.level=='level_01':
            self.is_level=True
        else:
            self.is_level=False

    department = fields.Many2one('hr.department',string='部门')
    is_level = fields.Boolean( string="是否一级",readonly=True)

    @api.model
    def create(self, vals):
        if vals['level']=='level_02':
            if not vals['department']:
                raise ValidationError('请填写部门')
            resul = self.search([('pro_state','=',vals['pro_state']),('level','=','level_02'),('department','=',vals['department'])])
            if len(resul)>0:
                raise ValidationError('二级审批只有一个')
        result = super(dtdream_rd_approver, self).create(vals)
        return  result


#审批意见
class dtdream_rd_process(models.Model):
    _name = 'dtdream_rd_process'
    pro_state = fields.Selection([('state_01','立项'),('state_02','总体设计')],string='阶段', readonly=True)
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
    reason =  fields.Text("意见")

    process_id = fields.Many2one('dtdream_prod_appr',string='研发产品')
    ztsj_process_id = fields.Many2one('dtdream_prod_appr',string='研发产品')

    is_new = fields.Boolean(string="标记是否为新",default=True)

    @api.model
    def _compute_editable(self):
        for rec in self:
            if rec.pro_state=='state_01':
                if rec.level=='level_01':
                    if rec.process_id.state==rec.pro_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new and not rec.process_id.is_finsished_01:
                        rec.editable=True
                    else:
                        rec.editable=False
                if rec.level=='level_02':
                    if rec.process_id.state==rec.pro_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new:
                        rec.editable=True
                    else:
                        rec.editable=False
            else:
                if rec.level=='level_01':
                    if rec.ztsj_process_id.state==rec.pro_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new and not rec.ztsj_process_id.is_finsished_02:
                        rec.editable=True
                    else:
                        rec.editable=False
                if rec.level=='level_02':
                    if rec.ztsj_process_id.state==rec.pro_state and rec.approver.user_id.id ==self.env.user.id and rec.is_new:
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



