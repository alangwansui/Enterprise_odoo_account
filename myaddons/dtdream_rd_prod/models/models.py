# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.osv import expression
from datetime import datetime
import threading
from time import sleep
from openerp.api import Environment
mutex = threading.Lock()
class dtdream_rd_prod(models.Model):
    _name = 'dtdream_rd_prod'
    name = fields.Char("项目名称")
    code = fields.Char("项目编码")


#研发产品
class dtdream_prod_appr(models.Model):
    _name = 'dtdream_prod_appr'
    _inherit = ['mail.thread']
    _description = u"研发产品"
    department = fields.Many2one('hr.department','部门',track_visibility='onchange',required=True)
    department_2 = fields.Many2one('hr.department','二级部门',track_visibility='onchange')
    name=fields.Char('产品名称',required=True,track_visibility='onchange')


    state = fields.Selection([('state_00','草稿'),('state_01','立项'),('state_02','总体设计'),('state_03','迭代开发'),('state_04','验证发布'),('state_06','暂停'),('state_07','中止'),('state_05','完成')],'产品状态',readonly=True,default='state_00')

    state_old = fields.Selection([('state_00','草稿'),('state_01','立项'),('state_02','总体设计'),('state_03','迭代开发'),('state_04','验证发布'),('state_05','完成'),('state_06','暂停'),('state_07','中止')])

    version_ids = fields.One2many('dtdream_rd_version','proName','版本')
    role_ids = fields.One2many('dtdream_rd_role','role_id',string='角色')

    pro_time = fields.Date('立项时间',track_visibility='onchange')
    overall_plan_time = fields.Date('总体设计计划完成时间',track_visibility='onchange')
    overall_actual_time = fields.Date('总体设计实际完成时间',track_visibility='onchange')

    start_pro_mar = fields.Text('立项材料',track_visibility='onchange')
    overall_mar = fields.Text('总体设计材料',track_visibility='onchange')

    cg_finsh_time = fields.Datetime(string="草稿阶段完成时间")
    lx_finsh_time = fields.Datetime(string="立项阶段完成时间")
    ztsj_finsh_time = fields.Datetime(string="总体设计阶段完成时间")
    ddfb_finsh_time = fields.Datetime(string="迭代发布阶段完成时间")
    yzfb_finsh_time = fields.Datetime(string="验证发布阶段完成时间")

    @api.multi
    def _compute_employee(self):
        role = self.env["dtdream_rd_config"].search([("name", "=", u"PDT经理")])
        for recc in self:
            for rec in recc.role_ids:
                if role ==rec.cof_id:
                    if rec.person:
                        recc.PDT=rec.person.id

    PDT = fields.Many2one("hr.employee",string="PDT经理",compute=_compute_employee)



    color = fields.Integer('Color Index')
    active = fields.Boolean(default=True)

    process_ids = fields.One2many('dtdream_rd_process','process_id',string="立项审批意见",track_visibility='onchange')

    ztsj_process_ids = fields.One2many('dtdream_rd_process','ztsj_process_id',string="总体设计审批意见",track_visibility='onchange')

    @api.one
    def _compute_liwai_log(self):
        cr = self.env["dtdream_execption"].search([("name.id", "=", self.id)])
        self.liwai_nums = len(cr)

    liwai_nums = fields.Integer(compute='_compute_liwai_log', string="例外记录",store=True)

    @api.one
    def _compute_dept(self):
        em = self.env['hr.employee'].search([('user_id','=',self.env.uid)])
        if em.department_id.id == self.department_2.id:
            self.sameDept=True
        else:
            self.sameDept=False
    sameDept = fields.Boolean(string="是否同一部门",compute=_compute_dept,store=True,default=False)

    def add_follower(self, cr, uid, ids, employee_id, context=None):
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        if employee and employee.user_id:
            self.message_subscribe_users(cr, uid, ids, user_ids=[employee.user_id.id], context=context)

    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True, mail_create_nosubscribe=True)
        prod_id = super(dtdream_prod_appr, self).create(cr, uid, values, context=context)
        self.message_subscribe_users(cr, uid, [prod_id],user_ids=[uid], context=context)
        return prod_id

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    @api.constrains('process_ids')
    def _compute_process_ids(self):
        for process in self.process_ids:
            if process.approver_old and process.approver!=process.approver_old:
                if self.department_2:
                    subject=process.approver_old.name+u"把"+self.department.name+u"/"+self.department_2.name+u"的"+self.name+u"审批权限授予你"
                    content = process.approver_old.name+u"把"+self.department_2.name+u"的"+self.name+u"审批权限授予你"
                else:
                    subject=process.approver_old.name+u"把"+self.department.name+u"的"+self.name+u"审批权限授予你"
                    content = process.approver_old.name+u"把"+self.department.name+u"的"+self.name+u"审批权限授予你"
                appellation = process.approver.name+u",您好"

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
                    'email_to': '%s' % process.approver.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()
                self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作人</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name,process.approver_old.name,u'将审批权限授给'+process.approver.name))
                process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                self.write({'current_approver_user': [(4,process.approver.user_id.id)]})
                self.add_follower(employee_id=process.approver.id)

    @api.constrains('ztsj_process_ids')
    def _compute_ztsj_process_ids(self):
        for process in self.ztsj_process_ids:
            if process.approver_old and process.approver!=process.approver_old:
                if self.department_2:
                    subject=process.approver_old.name+u"把"+self.department.name+u"/"+self.department_2.name+u"的"+self.name+u"审批权限授予你"
                    content = process.approver_old.name+u"把"+self.department_2.name+u"的"+self.name+u"审批权限授予你"
                else:
                    subject=process.approver_old.name+u"把"+self.department.name+u"的"+self.name+u"审批权限授予你"
                    content = process.approver_old.name+u"把"+self.department.name+u"的"+self.name+u"审批权限授予你"
                appellation = process.approver.name+u",您好"
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
                    'email_to': '%s' % process.approver.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()
                self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作人</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name,process.approver_old.name,u'将审批权限授给'+process.approver.name))
                process.write({'is_pass':False,'is_refuse':False,'is_risk':False,'approver_old':process.approver.id})
                self.write({'current_approver_user': [(4,process.approver.user_id.id)]})
                self.add_follower(employee_id=process.approver.id)

    is_finsished_01 = fields.Boolean(string="立项多人审批是否结束",store=True)
    is_finsished_02 = fields.Boolean(string="总体设计多人审批是否结束",store=True)

    current_approver_user = fields.Many2many("res.users", "c_a_u_u",string="当前审批人用户")

    his_app_user = fields.Many2many("res.users" ,"h_a_u_u",string="历史审批人用户")


    @api.onchange('message_follower_ids')
    def _compute_follower(self):
        self.followers_user = False
        for foll in self.message_follower_ids:
            self.write({'followers_user': [(4,foll.partner_id.user_ids.id)]})
            if foll.partner_id.user_ids not in self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users and foll.partner_id.user_ids not in self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").users:
                self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").sudo().write({'users': [(4,foll.partner_id.user_ids.id)]})

    followers_user = fields.Many2many("res.users" ,"f_u_u",string="关注者")
    is_appred = fields.Boolean(string="标识总体设计阶段提交按钮",default=False)
    is_lixiangappred = fields.Boolean(string="标识立项阶段提交按钮",default=False)


    #关注者删除方法重写
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

    @api.one
    def _compute_create(self):
        role = self.env["dtdream_rd_config"].search([("name", "=", u"PDT经理")])
        pdt = False
        for rec in self.role_ids:
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
        if self.env.user in users:
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

    @api.multi
    def _wkf_message_post(self,statechange):
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name,statechange))

#流程方法
    @api.model
    def wkf_draft(self):
        if self.state=='state_01':
            self.write({'is_lixiangappred':False})
            self.write({'is_appred':False})
            self.write({'is_finsished_01':False})
            processes = self.env['dtdream_rd_process'].search([('process_id','=',self.id)])
            processes.unlink()
            self._wkf_message_post(statechange=u'产品状态: 立项->草稿')
        elif self.state=='state_06':
            self._wkf_message_post(statechange=u'产品状态: 暂停->草稿')
        elif self.state=='state_07':
            self._wkf_message_post(statechange=u'产品状态: 中止->草稿')
        self.write({'state': 'state_00'})
        self.current_approver_user = [(5,)]

    @api.multi
    def wkf_lixiang(self):
        self.message_follower_ids
        if self.state=="state_02":
            self.write({'is_lixiangappred':False})
            self.write({'is_appred':False})
            self.write({'is_finsished_01':False,'is_finsished_02':False})
            processes = self.env['dtdream_rd_process'].search([('process_id','=',self.id)])
            processes.unlink()
            ztsj_processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',self.id)])
            ztsj_processes.unlink()
            self._wkf_message_post(statechange=u'产品状态: 总体设计->立项')
        elif self.state=='state_06':
            self._wkf_message_post(statechange=u'产品状态: 暂停->立项')
        elif self.state=='state_07':
            self._wkf_message_post(statechange=u'产品状态: 中止->立项')
        elif self.state=='state_00':
            self._wkf_message_post(statechange=u'产品状态: 草稿->立项')
            self.write({'cg_finsh_time':datetime.now()})
        self.write({'state': 'state_01'})

    @api.multi
    def wkf_ztsj(self):
        if self.state=="state_03":
            self.write({'is_appred':False})
            self.write({'is_finsished_02':False})
            ztsj_processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',self.id)])
            ztsj_processes.unlink()
            self._wkf_message_post(statechange=u'产品状态: 迭代开发->总体设计')
        elif self.state=='state_06':
            self._wkf_message_post(statechange=u'产品状态: 暂停->总体设计')
        elif self.state=='state_07':
            self._wkf_message_post(statechange=u'产品状态: 中止->总体设计')
        elif self.state=='state_01':
            self._wkf_message_post(statechange=u'产品状态: 立项->总体设计')
            self.write({'lx_finsh_time':datetime.now()})
        self.write({'state': 'state_02'})

    @api.multi
    def wkf_ddkf(self):
        if self.state=="state_02":
            self._wkf_message_post(statechange=u'产品状态: 总体设计->迭代开发')
            self.write({'ztsj_finsh_time':datetime.now()})
        elif self.state=='state_06':
            self._wkf_message_post(statechange=u'产品状态: 暂停->迭代开发')
        elif self.state=='state_07':
            self._wkf_message_post(statechange=u'产品状态: 中止->迭代开发')
        if self.state=="state_04":
            self._wkf_message_post(statechange=u'产品状态: 验证发布->迭代开发')
        self.write({'state': 'state_03'})

    @api.multi
    def wkf_yzfb(self):
        if self.state=="state_03":
            self._wkf_message_post(statechange=u'产品状态: 迭代开发->验证发布')
            self.write({'ddfb_finsh_time':datetime.now()})
        elif self.state=='state_06':
            self._wkf_message_post(statechange=u'产品状态: 暂停->验证发布')
        elif self.state=='state_07':
            self._wkf_message_post(statechange=u'产品状态: 中止->验证发布')
        if self.state=="state_05":
            self._wkf_message_post(statechange=u'产品状态: 完成->验证发布')
        self.write({'state': 'state_04'})

    @api.multi
    def wkf_jieshu(self):
        if self.state=="state_04":
            self._wkf_message_post(statechange=u'产品状态: 验证发布->完成')
            self.write({'yzfb_finsh_time':datetime.now()})
        elif self.state=='state_06':
            self._wkf_message_post(statechange=u'产品状态: 暂停->完成')
        elif self.state=='state_07':
            self._wkf_message_post(statechange=u'产品状态: 中止->完成')
        self.write({'state': 'state_05'})

    @api.multi
    def wkf_zanting(self):
        if self.state=='state_00':
            self._wkf_message_post(statechange=u'产品状态: 草稿->暂停')
        elif self.state=='state_01':
            self._wkf_message_post(statechange=u'产品状态: 立项->暂停')
        elif self.state=='state_02':
            self._wkf_message_post(statechange=u'产品状态: 总体设计->暂停')
        elif self.state=='state_03':
            self._wkf_message_post(statechange=u'产品状态: 迭代开发->暂停')
        elif self.state=='state_04':
            self._wkf_message_post(statechange=u'产品状态: 验证发布->暂停')
        elif self.state=='state_05':
            self._wkf_message_post(statechange=u'产品状态: 完成->暂停')
        elif self.state=='state_07':
            self._wkf_message_post(statechange=u'产品状态: 中止->暂停')
        self.write({'state':'state_06'})


    @api.multi
    def wkf_zhongzhi(self):
        if self.state=='state_00':
            self._wkf_message_post(statechange=u'产品状态: 草稿->中止')
        elif self.state=='state_01':
            self._wkf_message_post(statechange=u'产品状态: 立项->中止')
        elif self.state=='state_02':
            self._wkf_message_post(statechange=u'产品状态: 总体设计->中止')
        elif self.state=='state_03':
            self._wkf_message_post(statechange=u'产品状态: 迭代开发->中止')
        elif self.state=='state_04':
            self._wkf_message_post(statechange=u'产品状态: 验证发布->中止')
        elif self.state=='state_05':
            self._wkf_message_post(statechange=u'产品状态: 完成->中止')
        elif self.state=='state_06':
            self._wkf_message_post(statechange=u'产品状态: 暂停->中止')
        self.write({'state':'state_07'})

    #返回上一部
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

    def yyy(self, qa_user, follower,user_all,journey):
        mutex.acquire()
        with Environment.manage():
            for i in range(len(journey)):
                if journey[i] not in qa_user and journey[i] not in user_all:
                    self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").sudo().write({'users': [(4, journey[i])]})
                if journey[i] not in follower:
                    self.message_subscribe_users(user_ids=[journey[i]])
            # sleep(1)
        mutex.release()

    @api.constrains('role_ids')
    def _com_role_ids(self):
        follower = [x.partner_id.user_ids.id for x in self.message_follower_ids]
        qa_user = [x.id for x in self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users]
        user_all = [x.id for x in self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").users]
        role = self.env["dtdream_rd_config"].search([("name", "=", u"PDT经理")])
        for rec in self.role_ids:
            if role ==rec.cof_id:
                if rec.person:
                    self.write({'PDT':rec.person.id})
                    break
        role_ids = self.role_ids
        for index, journey in enumerate(self.role_ids):
            for j in range(index):
                if journey.cof_id == self.role_ids[j].cof_id:
                    raise ValidationError(u"角色不能重复")


        # roles_ids 去重
        person = []
        roles_ids_person = [x.person.user_id.id for x in self.role_ids]
        for pers in roles_ids_person:
            if pers not in person and pers:
                person.append(pers)

        xxx = [[],[],[],[]]
        for index, journey in enumerate(person):
            num = index % 4
            xxx[num].append(journey)

        #起线程 4 或者 <4
        tt = []
        for i in range(4):
            if len(xxx[i])>0:
                t = threading.Thread(target=self.yyy, args=(qa_user, follower, user_all, xxx[i]))
                tt.append(t)

        for i in range(len(tt)):
            tt[i].start()
        for i in range(len(tt)):
            tt[i].join()

        exceptions = self.env["dtdream_execption"].search([('name', '=',self.id)])
        for exception in exceptions:
            exception.role_person = [(5,)]
            for role in self.role_ids:
                exception.write({'role_person': [(4,role.person.user_id.id)]})

    @api.multi
    def do_cgtj(self):
        if self.state=='state_00':
            self.signal_workflow('btn_to_lixiang')

    #下一步
    @api.multi
    def do_next(self):
        if self.state=='state_03':
            self.signal_workflow('btn_to_yzfb')

    #结束
    @api.multi
    def do_jieshu(self):
        self.signal_workflow('btn_to_jieshu')

    #总体设计提交
    @api.multi
    def do_ztsjtj(self):
        if self.state=="state_02":
            self.write({'is_appred':True})
            self.current_approver_user = [(5,)]
            records = self.env['dtdream_rd_approver'].search([('pro_state','=','state_02'),('level','=','level_01')])           #审批人配置
            rold_ids = []
            for record in records:
                rold_ids +=[record.name.id]
            appro = self.env['dtdream_rd_role'].search([('role_id','=',self.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
            for record in appro:
                self.env['dtdream_rd_process'].create({"role":record.cof_id.id, "ztsj_process_id":self.id,'pro_state':'state_02','approver':record.person.id,'approver_old':record.person.id,'level':'level_01'})       #审批意见记录创建
                self.write({'current_approver_user': [(4, record.person.user_id.id)]})
                if self.department_2:
                    subject=self.department.name+u"/"+self.department_2.name+u"的"+self.name+u"待您的审批"
                else:
                    subject=self.department.name+u"的"+self.name+u"待您的审批"
                appellation = record.person.name+u",您好"
                content = self.department.name+u"的"+self.name+u"已进入总体设计阶段，等待您的审批"
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
                    'email_to': '%s' % record.person.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()

            processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',self.id),('pro_state','=','state_02'),('level','=','level_01'),('is_new','=',True)])
            if len(processes)==0:
                records = self.env['dtdream_rd_approver'].search([('pro_state','=',self.state),('level','=','level_02')])           #审批人配置
                rold_ids = []
                for record in records:
                    rold_ids +=[record.name.id]
                appro = self.env['dtdream_rd_role'].search([('role_id','=',self.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                if len(appro)==0:
                    self.write({'overall_actual_time':datetime.now()})
                    self.signal_workflow('btn_to_ddkf')
                else:
                    self.current_approver_user = [(5,)]
                    for record in appro:
                        self.env['dtdream_rd_process'].create({"role":record.cof_id.id, "process_id":self.id,'pro_state':self.state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_02'})       #审批意见记录创建
                        self.write({'current_approver_user': [(4, record.person.user_id.id)]})
                        if self.department_2:
                            subject=self.department.name+u"/"+self.department_2.name+u"的"+self.name+u"待您的审批"
                        else:
                            subject=self.department.name+u"的"+self.name+u"待您的审批"
                        appellation = record.person.name+u",您好"
                        content = self.department.name+u"的"+self.name+u"已进入总体设计阶段，等待您的审批"
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
                            'email_to': '%s' % record.person.work_email,
                            'auto_delete': False,
                            'email_from':self.get_mail_server_name(),
                        }).send()

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

    @api.constrains('agree')
    def _com_agree(self):
        if self.is_zhongzhi and self.agree:
            if self.state=='state_00':
                self.state_old='state_00'
                self.signal_workflow('draft_to_zhongzhi')
            if self.state=='state_01':
                self.state_old='state_01'
                self.signal_workflow('lixiang_to_zhongzhi')
            if self.state=='state_02':
                self.state_old='state_02'
                self.signal_workflow('ztsj_to_zhongzhi')
            if self.state=='state_03':
                self.state_old='state_03'
                self.signal_workflow('ddkf_to_zhongzhi')
            if self.state=='state_04':
                self.state_old='state_04'
                self.signal_workflow('yzfb_to_zhongzhi')
            if self.state=='state_06':
                self.state_old='state_06'
                self.signal_workflow('zanting_to_zhongzhi')
            self.write({'is_zhongzhi':False,'is_zhongzhitj':False})
        elif not self.is_zhongzhi and self.is_zanting and self.agree:
            if self.state=='state_00':
                self.state_old='state_00'
                self.signal_workflow('draft_to_zanting')
            if self.state=='state_01':
                self.state_old='state_01'
                self.signal_workflow('lixiang_to_zanting')
            if self.state=='state_02':
                self.state_old='state_02'
                self.signal_workflow('ztsj_to_zanting')
            if self.state=='state_03':
                self.state_old='state_03'
                self.signal_workflow('ddkf_to_zanting')
            if self.state=='state_04':
                self.state_old='state_04'
                self.signal_workflow('yzfb_to_zanting')
            self.write({'is_zanting':False,'is_zantingtj':False})

        if self.is_zanting_back and self.agree:
            if self.state_old=='state_00':
                self.signal_workflow('zanting_to_draft')
            if self.state_old=='state_01':
                self.signal_workflow('zanting_to_lixiang')
            if self.state_old=='state_02':
                self.signal_workflow('zanting_to_ztsj')
            if self.state_old=='state_03':
                self.signal_workflow('zanting_to_ddkf')
            if self.state_old=='state_04':
                self.signal_workflow('zanting_to_yzfb')
            self.write({'is_zanting_back':False,'is_zanting_backtj':False})
        if self.comments and self.agree:
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">审批人</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name,self.department.manager_id.name,u'审批意见:同意,意见：'+self.comments))


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
                                       <tr><td style="padding:10px">审批人</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name,self.department.manager_id.name,u'审批意见:不同意,意见：'+self.comments))
    #申请暂停
    @api.multi
    def do_zanting(self):
        if self.is_lixiangappred or self.is_appred:
            raise ValidationError('已提交审批，不能申请暂停')
        self.write({'reason_request':'','agree':False,'disagree':False,'comments':'','is_zanting':True,'is_ztpage':True})

    #提交暂停
    @api.multi
    def do_zantingtj(self):
        if self.disagree:
            self.write({'disagree':'','comments':''})
        if self.reason_request:
            # if not self.department.manager_id:
            #     raise ValidationError(u"请配置%s的部门主管" %(self.department.name))
            is_plccb = False
            plccb=None
            for role in self.role_ids:
                if role.cof_id.name=="PL-CCB":
                    is_plccb=True
                    plccb=role.person
                    break
            if not is_plccb or not plccb:
                raise ValidationError(u"该产品没有配置PL-CCB")
            self.write({'is_zantingtj':True})
            self.current_approver_user = [(5,)]
            # self.add_follower(employee_id=self.department.manager_id.id)
            if self.department_2:
                subject=self.department.name+u"/"+self.department_2.name+u"的"+self.name+u"待您的审批"
            else:
                subject=self.department.name+u"的"+self.name+u"待您的审批"
            appellation = plccb.name+u",您好"
            content = self.department.name+u"的"+self.name+u"的暂停申请，待您审批"
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
                'email_to': '%s' % plccb.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()
            self.write({'current_approver_user': [(4,plccb.user_id.id)]})
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name,u'提交暂停',self.reason_request))
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
            for role in self.role_ids:
                if role.cof_id.name=="PL-CCB":
                    is_plccb=True
                    plccb=role.person
                    break
            if not is_plccb or not plccb:
                raise ValidationError(u"该产品没有配置PL-CCB")
            self.write({'is_zanting_backtj':True})
            self.current_approver_user = [(5,)]
            # if not self.department.manager_id:
            #     raise ValidationError(u"请配置%s的部门主管" %(self.department.name))
            if self.department_2:
                subject=self.department.name+u"/"+self.department_2.name+u"的"+self.name+u"待您的审批"
            else:
                subject=self.department.name+u"的"+self.name+u"待您的审批"
            appellation = plccb.name+u",您好"
            content = self.department.name+u"的"+self.name+u"的恢复暂停申请，待您审批"
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
                'email_to': '%s' % plccb.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()
            self.write({'current_approver_user': [(4,plccb.user_id.id)]})
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name,u'恢复暂停',self.reason_request))
        else:
            raise ValidationError('申请原因未填写')

    #申请中止
    @api.multi
    def do_zhongzhi(self):
        if self.is_lixiangappred or self.is_appred:
            raise ValidationError('已提交审批，不能申请中止')
        self.write({'reason_request':'','agree':False,'disagree':False,'comments':'','is_zhongzhi':True,'is_ztpage':True})

    #中止提交
    @api.multi
    def do_zhongzhitj(self):
        if self.disagree:
            self.write({'disagree':'','comments':''})
        if self.reason_request:
            is_plccb = False
            plccb=None
            for role in self.role_ids:
                if role.cof_id.name=="PL-CCB":
                    is_plccb=True
                    plccb=role.person
                    break
            if not is_plccb or not plccb:
                raise ValidationError(u"该产品没有配置PL-CCB")
            self.write({'is_zhongzhitj':True})
            self.current_approver_user = [(5,)]
            if self.department_2:
                subject=self.department.name+u"/"+self.department_2.name+u"的"+self.name+u"待您的审批"
            else:
                subject=self.department.name+u"的"+self.name+u"待您的审批"
            appellation = plccb.name+u",您好"
            content = self.department.name+u"的"+self.name+u"的中止申请，待您审批"
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
                'email_to': '%s' % plccb.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()
            self.write({'current_approver_user': [(4,plccb.user_id.id)]})
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name,u'提交中止',self.reason_request))
        else:
            raise ValidationError('申请原因未填写')

    #中止恢复
    @api.multi
    def do_zhongzhi_back(self):
        if self.state_old=='state_00':
            self.signal_workflow('zhongzhi_to_draft')
        if self.state_old=='state_01':
            self.signal_workflow('zhongzhi_to_lixiang')
        if self.state_old=='state_02':
            self.signal_workflow('zhongzhi_to_ztsj')
        if self.state_old=='state_03':
            self.signal_workflow('zhongzhi_to_ddkf')
        if self.state_old=='state_04':
            self.signal_workflow('zhongzhi_to_yzfb')
        if self.state_old=='state_06':
            self.signal_workflow('zhongzhi_to_zanting')
        self.write({'reason_request':'','agree':False,'disagree':False,'comments':''})

    execption_id = fields.Many2one('dtdream_execption',string="待提交例外")
    execption_flag = fields.Boolean(string="标记是否存在未提交例外")


    def action_makeexception(self, cr, uid, ids, context=None):
        opportunity = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'dtdream_rd_prod', 'act_dtdream_exceptionedit', context)
        res['context'] = {
            'default_name': opportunity.execption_id.name.id,
            'default_version': opportunity.execption_id.version.id,
            'default_reason': opportunity.execption_id.reason,
            'default_approver_fir': opportunity.execption_id.approver_fir.id,
            'default_approver_sec': opportunity.execption_id.approver_sec.id,
            'default_mark':True
        }
        return res


    #提交例外
    @api.multi
    def execptiontj(self):
        if not self.approver_fir:
            raise ValidationError(u"第一审批人不能为空")
        if self.department_2:
            subject=self.department.name+u"/"+self.department_2.name+u"的"+self.name+u"待您的审批"
        else:
            subject=self.department.name+u"的"+self.name+u"待您的审批"
        appellation = self.department.manager_id.name+u",您好"
        content = self.department.name+u"的"+self.name+u"的例外申请，待您审批"
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
                domain = expression.AND([['|','|','|','|','|',('department','=',em.department_id.id),('department_2','=',em.department_id.id),('create_uid','=',uid),('current_approver_user','=',uid),('his_app_user','=',uid),('followers_user','=',uid)], domain])
        res = super(dtdream_prod_appr, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
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
                domain = expression.AND([['|','|','|','|','|',('department','=',em.department_id.id),('department_2','=',em.department_id.id),('create_uid','=',uid),('current_approver_user','=',uid),('his_app_user','=',uid),('followers_user','=',uid)], domain])
        return super(dtdream_prod_appr, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)


    def process_email_send(self,product,process,state):
        subject=u'请尽快处理'+product.name+u'产品'+state+u'状态审批！'
        appellation = process.approver.name+u",您好"
        content = product.name+u'产品'+state+u'状态的审批您还未处理，请及时处理！'
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % product.id
        url = base_url+link
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,product.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % process.approver.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()

    def special_send_email(self,product,state):
        subject=u'请尽快处理'+product.name+u'产品申请'+state+u'审批！'
        appellation = product.department.maneger_id.name+u",您好"
        content = product.name+u'产品申请'+state+u'的审批您还未处理，请及时处理！'
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % product.id
        url = base_url+link
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,product.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % product.department.maneger_id.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()


    #定时发送邮件提醒
    @api.model
    def timing_send_email(self):
        products=self.env['dtdream_prod_appr'].sudo().search([('state','not in',('state_00','state_05','state_07'))])
        for product in products:
            if product.state=="state_01":
                if product.is_lixiangappred:
                    for process in product.process_ids:
                        if ( not process.is_pass and not process.is_risk):
                            self.process_email_send(product=product,process=process,state=u"立项")
                elif product.is_zhongzhitj:
                    self.special_send_email(product=product,state=u"中止")
                elif product.is_zantingtj and not product.is_zhongzhitj:
                     self.special_send_email(product=product,state=u"暂停")
            elif product.state=="state_02":
                if product.is_appred:
                    for process in product.ztsj_process_ids:
                        if ( not process.is_pass and not process.is_risk):
                            self.process_email_send(product=product,process=process,state=u'总体设计')
                elif product.is_zhongzhitj:
                    self.special_send_email(product=product,state=u"中止")
                elif product.is_zantingtj and not product.is_zhongzhitj:
                     self.special_send_email(product=product,state=u"暂停")
            elif product.state=="state_03" or product.state=="state_04":
                if product.is_zhongzhitj:
                    self.special_send_email(product=product,state=u"中止")
                elif product.is_zantingtj and not product.is_zhongzhitj:
                     self.special_send_email(product=product,state=u"暂停")
            elif product.state=="state_04":
                if product.is_zhongzhitj:
                    self.special_send_email(product=product,state=u"中止")
                elif product.is_zanting_backtj:
                     self.special_send_email(product=product,state=u"恢复暂停")

    @api.model
    def default_get(self, fields):
        rec = super(dtdream_prod_appr, self).default_get(fields)
        results = self.env['dtdream_rd_config'].sudo().search([])
        list=[]
        list.append((6,0,[]))
        for reuslt in results:
            lit = {'cof_id':reuslt.id,'person':reuslt.person.id}
            list.append((0,0,lit))
        rec.update({'role_ids': list})
        return rec

#角色基础配置
class dtdream_rd_config(models.Model):
    _name = 'dtdream_rd_config'
    name = fields.Char('角色名称')
    person = fields.Many2one("hr.employee",'人员')
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
    # _rec_name ="person"
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

    @api.multi
    def name_get(self):
        res = super(dtdream_rd_role, self).name_get()
        data = []
        for role in self:
            display_value = ''
            display_value += role.cof_id.name or ""
            display_value += ' '
            display_value += role.person.name or ""
            data.append((role.id, display_value))
        return data

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, ['|',('cof_id', 'ilike', name),('person', 'ilike', name)] + args, limit=limit)
        return super(dtdream_rd_role, self).name_search(
            cr, user, '', args=[('id', 'in', list(ids))],
            operator='ilike', context=context, limit=limit)


#产品审批基础数据配置
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



#产品审批意见
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




#例外
class dtdream_execption(models.Model):
    _name = "dtdream_execption"
    _inherit =['mail.thread']
    _description = "例外"
    name=fields.Many2one("dtdream_prod_appr" ,required=True,string="产品名称")
    version = fields.Many2one("dtdream_rd_version",string="版本")
    reason = fields.Text(string="例外原因",track_visibility='onchange')
    state= fields.Selection([('dsp','待审批'),('yjsp','一级审批'),('Nyjsp','一级审批不通过'),('ejsp','二级审批'),('Nejsp','二级审批不通过'),('ysp','已审批')],string="状态",default='dsp')
    flag = fields.Boolean(string="标记保存取消按钮是否可见")
    mark = fields.Boolean(string="用于区分是从产品还是版本")
    is_apped = fields.Boolean(string="标记是否提交")

    approver_fir = fields.Many2one("hr.employee" ,string="第一审批人")
    approver_sec = fields.Many2one("hr.employee",string="第二审批人")

    agree = fields.Boolean(string="同意")

    def add_follower(self, cr, uid, ids, employee_id, context=None):
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        if employee and employee.user_id:
            self.message_subscribe_users(cr, uid, ids, user_ids=[employee.user_id.id], context=context)

    @api.constrains('approver_fir')
    def _conp_approver_fir(self):
        if self.approver_fir:
            self.add_follower(employee_id=self.approver_fir.id)

    @api.constrains('approver_sec')
    def _conp_approver_sec(self):
        if self.approver_sec:
            self.add_follower(employee_id=self.approver_sec.id)

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

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    #产品申请例外提交
    @api.multi
    def btn_execption_submit(self):
        res= self.write({'name':self.name.id,'version':self.version.id,'reason':self.reason,'state':'dsp','flag':True,'is_apped':True})
        if not self.reason:
            raise ValidationError(u'例外原因不能为空')
        if self.mark:
            if not self.approver_fir:
                raise ValidationError(u"第一审批人不能为空")
            if self.name.department_2:
                subject=self.name.department.name+u"/"+self.name.department_2.name+u"的"+self.name.name+u"的例外申请，待您审批"
            else:
                subject=self.name.department.name+u"的"+self.name.name+u"的例外申请，待您审批"
            appellation = self.approver_fir.name+u",您好"
            content = self.name.department.name+u"的"+self.name.name+u"的例外申请，待您审批"
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream_execption' % self.id
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
            self.current_approver_user = [(5,)]
            self.write({'state':'yjsp','current_approver_user':[(4,self.approver_fir.user_id.id)]})
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">动作</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name.name,u'例外提交',u'状态变化：草稿->一级审批；申请原因：'+self.reason))
        else:
            if not self.approver_fir:
                raise ValidationError(u"第一审批人不能为空")
            if self.name.department_2:
                subject=self.name.department.name+u"/"+self.name.department_2.name+u"的"+self.name.name+u"的"+self.version.version_numb+u"待您审批"
            else:
                subject=self.name.department.name+u"的"+self.name.name+u"的"+self.version.version_numb+u"待您审批"
            appellation = self.approver_fir.name+u",您好"
            content = self.name.department.name+u"的"+self.name.name+u"的"+self.version.version_numb+u"的例外申请，待您审批"
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream_execption' % self.id
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
            self.current_approver_user = [(5,)]
            self.write({'state':'yjsp','current_approver_user':[(4,self.approver_fir.user_id.id)]})
            self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">动作</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name.name,u'例外提交',u'状态变化：草稿->一级审批；申请原因：'+self.reason))
        return res


    @api.multi
    def execptiontj(self):
        self.write({'is_apped':True})
        if not self.reason:
            raise ValidationError(u'例外原因不能为空')
        if not self.approver_fir:
            raise ValidationError(u"第一审批人不能为空")
        if self.name.department_2:
            subject=self.name.department.name+u"/"+self.name.department_2.name+u"的"+self.name.name+u"的例外申请，待您审批"
        else:
            subject=self.name.department.name+u"的"+self.name.name+u"的例外申请，待您审批"
        appellation = self.approver_fir.name+u",您好"
        content = self.name.department.name+u"的"+self.name.name+u"的例外申请，待您审批"
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream_execption' % self.id
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
        self.current_approver_user = [(5,)]
        self.write({'state':'yjsp','current_approver_user':[(4,self.approver_fir.user_id.id)]})
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                       <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                       <tr><td style="padding:10px">动作</td><td style="padding:10px">%s</td></tr>
                                       <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                       </table>""" %(self.name.name,u'例外提交',u'状态变化：草稿->一级审批；申请原因：'+self.reason))

    @api.multi
    def do_agree(self):
        if self.state=='yjsp':
            if self.approver_sec:
                self.write({'state':'ejsp'})
                if self.name.department_2:
                    subject=self.name.department.name+u"/"+self.name.department_2.name+u"的"+self.name.name+u"的例外申请，待您审批"
                else:
                    subject=self.name.department.name+u"的"+self.name.name+u"的例外申请，待您审批"
                appellation = self.approver_fir.name+u",您好"
                content = self.name.department.name+u"的"+self.name.name+u"的例外申请，待您审批"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_execption' % self.id
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
                    'email_to': '%s' % self.approver_sec.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()
                self.current_approver_user = [(5,)]
                self.write({'current_approver_user':[(4,self.approver_sec.user_id.id)]})
                self.write({'agree':False,'comments':''})
            else:
                self.write({'state':'ysp'})
                self.current_approver_user = [(5,)]
        elif self.state=='ejsp':
            self.write({'state':'ysp'})
            self.current_approver_user = [(5,)]



    current_approver_user = fields.Many2many("res.users",string="当前审批人用户")
    @api.one
    def _compute_is_shenpiren(self):
        if self.env.user in self.current_approver_user:
            self.is_shenpiren=True
        else:
            self.is_shenpiren = False
    is_shenpiren = fields.Boolean(string="是否审批人",compute=_compute_is_shenpiren,readonly=True)

    @api.one
    def _compute_create(self):
        if self.create_uid==self.env.user:
            self.is_create=True
        else:
            self.is_create=False
    is_create = fields.Boolean(string="是否创建者",compute=_compute_create,store=True,default=True)

    @api.one
    def _compute_is_Qa(self):
        users =  self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users
        if self.env.user in users:
            self.is_Qa = True
        else:
            self.is_Qa=False
    is_Qa = fields.Boolean(string="是否在QA组",compute=_compute_is_Qa,readonly=True)


    role_person = fields.Many2many("res.users" ,"dtdream_execption_role_user",string="对应产品角色中的人员用户")

    his_app_user = fields.Many2many("res.users" ,"dtdream_execption_his_user",string="历史审批人用户")
    #
    @api.constrains('name')
    def con_name_role(self):
        self.role_person=[(5,)]
        for role in self.name.role_ids:
            if role.person:
                self.write({'role_person': [(4,role.person.user_id.id)]})



