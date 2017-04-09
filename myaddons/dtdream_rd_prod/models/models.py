# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.osv import expression
from datetime import datetime,timedelta
import threading
from openerp.api import Environment
mutex = threading.Lock()
from lxml import etree
class dtdream_rd_prod(models.Model):
    _name = 'dtdream_rd_prod'
    name = fields.Char("项目名称")
    code = fields.Char("项目编码")


#研发产品
class dtdream_prod_appr(models.Model):
    _name = 'dtdream_prod_appr'
    _inherit = ['mail.thread']
    _description = u"研发产品"
    department = fields.Many2one('hr.department', '部门', track_visibility='onchange', required=True)
    department_2 = fields.Many2one('hr.department', '二级部门', track_visibility='onchange')
    name = fields.Char('产品名称', required=True, track_visibility='onchange')
    pro_PDT = fields.Many2one('dtdream.rd.pdtconfig','PDT',track_visibility='onchange')
    state = fields.Selection([('state_00', '草稿'), ('state_01', '立项'), ('state_02', '总体设计'), ('state_03', '迭代开发'),
                              ('state_04', '验证发布'), ('state_06', '暂停'), ('state_07', '中止'), ('state_05', '完成')],'产品状态', readonly=True, default='state_00')

    state_old = fields.Selection([('state_00', '草稿'), ('state_01', '立项'), ('state_02', '总体设计'), ('state_03', '迭代开发'), ('state_04', '验证发布'),('state_05', '完成'),('state_06', '暂停'), ('state_07', '中止')])

    version_ids = fields.One2many('dtdream_rd_version', 'proName', '版本')
    role_ids = fields.One2many('dtdream_rd_role', 'role_id', string='角色')
    risk_ids = fields.One2many('dtdream_rd_risk', 'risk_id', string='风险与机遇', track_visibility='onchange')

    pro_time = fields.Date('立项时间', track_visibility='onchange')
    overall_plan_time = fields.Date('总体设计计划完成时间', track_visibility='onchange')
    overall_actual_time = fields.Date('总体设计实际完成时间', track_visibility='onchange')

    start_pro_mar = fields.Text('立项材料', track_visibility='onchange')
    overall_mar = fields.Text('总体设计材料', track_visibility='onchange')

    cg_finsh_time = fields.Datetime(string="草稿阶段完成时间")
    lx_finsh_time = fields.Datetime(string="立项阶段完成时间")
    ztsj_finsh_time = fields.Datetime(string="总体设计阶段完成时间")
    ddfb_finsh_time = fields.Datetime(string="迭代发布阶段完成时间")
    yzfb_finsh_time = fields.Datetime(string="验证发布阶段完成时间")

    @api.multi
    def _compute_employee(self):
        role = self.env["dtdream_rd_config"].search([("name", "=", u"PDT经理")])
        PL_CCB_role = self.env["dtdream_rd_config"].search([("name", "=", u"PL-CCB")])
        QA_role = self.env["dtdream_rd_config"].search([("name", "=", u"质量代表")])
        YF_role = self.env["dtdream_rd_config"].search([("name", "=", u"研发经理")])
        for recc in self:
            for rec in recc.role_ids:
                if role ==rec.cof_id:
                    if rec.person:
                        recc.PDT=rec.person.id
                if PL_CCB_role ==rec.cof_id:
                    if rec.person:
                        recc.PL_CCB=rec.person.id
                if QA_role ==rec.cof_id:
                    if rec.person:
                        recc.QA=rec.person.id
                if YF_role ==rec.cof_id:
                    if rec.person:
                        recc.YF_manager=rec.person.id


    PDT = fields.Many2one("hr.employee",string="PDT经理",compute=_compute_employee)
    PL_CCB = fields.Many2one("hr.employee", string="PL-CCB", compute=_compute_employee)
    QA = fields.Many2one("hr.employee", string="质量代表", compute=_compute_employee)
    YF_manager = fields.Many2one("hr.employee", string="研发经理", compute=_compute_employee)

    color = fields.Integer('Color Index')
    active = fields.Boolean(default=True)

    process_ids = fields.One2many('dtdream_rd_process','process_id',string="立项审批意见",track_visibility='onchange')

    ztsj_process_ids = fields.One2many('dtdream_rd_process','ztsj_process_id',string="总体设计审批意见",track_visibility='onchange')

    def _compute_liwai_log(self):
        cr = self.env["dtdream_execption"].search([("name.id", "=", self.id)])
        self.liwai_nums = len(cr)

    liwai_nums = fields.Integer(compute='_compute_liwai_log', string="例外记录")

    def _compute_zanting_log(self):
        cr = self.env["dtdream.prod.suspension"].search([("project.id", "=", self.id)])
        self.zanting_nums = len(cr)

    zanting_nums = fields.Integer(compute='_compute_zanting_log', string="暂停记录")

    Projectmagnitude = fields.Selection([('magnitude_00', 'NA'), ('magnitude_01', '重量级'), ('magnitude_02', '中量级'), ('magnitude_03', '轻量级')],string="项目量级")

    @api.one
    def _compute_dept(self):
        em = self.env['hr.employee'].search([('user_id','=',self.env.uid)])
        if em.department_id.id == self.department_2.id:
            self.sameDept=True
        else:
            self.sameDept=False
    sameDept = fields.Boolean(string="是否同一部门",compute=_compute_dept,default=False)

    def add_follower(self, cr, uid, ids, employee_id, context=None):
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        if employee and employee.user_id:
            self.message_subscribe_users(cr, uid, ids, user_ids=[employee.user_id.id], context=context)
            versions = self.pool.get("dtdream_rd_version").search(cr, uid, [('proName', '=', ids[0])],context=context)
            for version in versions:
                version = self.pool.get('dtdream_rd_version').browse(cr, uid, version, context=context)
                version.write({'followers_user': [(4, employee.user_id.id)]})

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

    # 获取抄送人邮箱
    def compute_email_list(self):
        people_email_list = ''
        appro = self.env['dtdream_rd_role'].search([('role_id', '=', self.id), ('person', '!=', False)])
        for record in appro:
            people_email_list += record.person.work_email + ';'
        return people_email_list

    @api.constrains('risk_ids')
    def _compute_risk_ids(self):
        email_list = self.compute_email_list()
        for process in self.risk_ids:
            is_change = process.is_risk_change()
            if is_change:
                # 记备注
                risk_sort_state_change = process.risk_sort_state_change()
                risk_state_change = process.risk_state_change()
                risk_PDT_change = process.risk_PDT_change()
                risk_plan_close_time_change = process.risk_plan_close_time_change()
                risk_chance_avoid_measure = process.risk_chance_avoid_measure()
                risk_chance_describe_change = process.risk_chance_describe_change()
                risk_name_change = process.risk_name_change()
                risk_description = process.name
                ins = u"<p>风险：%s 变更信息</p>%s%s%s%s%s%s%s"% (risk_description,
                                risk_name_change, risk_chance_describe_change, risk_chance_avoid_measure,risk_plan_close_time_change,
                                risk_PDT_change, risk_state_change, risk_sort_state_change)
                self.message_post(body=u"""%s""" % (ins))
                process.update_old_ins()
                # 发邮件
                subject = u"%s更新了风险信息，请查看" % (self.name)
                appellation = u"您好"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % self.id
                url = base_url + link
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                     %s
                                     <p>查看详情请点击链接:<a href="%s">%s</a></p>
                                    ''' % (appellation, ins, url, url),
                    'subject': '%s' % subject,
                    'email_to': '%s' % process.PDT.work_email,
                    'email_cc': '%s' % email_list,
                    'auto_delete': False,
                    'email_from': self.get_mail_server_name(),
                }).send()


    is_finsished_01 = fields.Boolean(string="立项多人审批是否结束",store=True)
    is_finsished_02 = fields.Boolean(string="总体设计多人审批是否结束",store=True)

    current_approver_user = fields.Many2many("res.users", "c_a_u_u",string="当前审批人用户")

    his_app_user = fields.Many2many("res.users" ,"h_a_u_u",string="历史审批人用户")

    @api.onchange('message_follower_ids')
    @api.constrains('message_follower_ids')
    def _compute_follower(self):
        # self.followers_user = False
        for foll in self.message_follower_ids:
            self.write({'followers_user': [(4,foll.partner_id.user_ids.id)]})
            if foll.partner_id.user_ids not in self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users and foll.partner_id.user_ids not in self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").users:
                self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").sudo().write({'users': [(4,foll.partner_id.user_ids.id)]})

    followers_user = fields.Many2many("res.users" ,"f_u_u",string="关注者")
    is_appred = fields.Boolean(string="标识总体设计阶段提交按钮",default=False)
    is_lixiangappred = fields.Boolean(string="标识立项阶段提交按钮",default=False)

    # #关注者添加方法重写
    # @api.multi
    # def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
    #     gen ,part = self.env['mail.followers']._add_follower_command(self._name, self.ids, {partner_ids[0]:None},{},True)
    #     self.sudo().write({'message_follower_ids': gen})


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
        if self.create_uid==self.env.user or pdt or self.env.user==self.YF_manager.user_id:
            self.is_create=True
        else:
            self.is_create=False
    is_create = fields.Boolean(string="是否创建者",compute=_compute_create,default=True)

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

    def _get_department_domain(self, rd_list=None):
        dm = []
        t = ('parent_id', '=', False)
        dm.append(t)
        for i in range(len(rd_list) - 1):
            dm.append('|')
        for i in range(len(rd_list)):
            dm.append(('name', '=', rd_list[i]))
        return dm

    def _get_department_2_domain(self, rd_list=None):
        dm_f = []
        t_f = ('parent_id.parent_id', '=', False)
        dm_f.append(t_f)
        for i in range(len(rd_list) - 1):
            dm_f.append('|')
        for i in range(len(rd_list)):
            dm_f.append(('parent_id.name', '=', rd_list[i]))
        return dm_f

#部门的联动
    @api.onchange('department_2')
    def _chang_department(self):
        domain = {}
        if self.department_2:
            self.department = self.department_2.parent_id
        else:
            try:
                rd_list = openerp.tools.config['rd_list'].split(',')
            except Exception, e:
                rd_list = []
            if len(rd_list) != 0:
                dm = self._get_department_domain(rd_list=rd_list)
                domain['department'] = dm
        return {'domain': domain}

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
                domain['department_2'] = self._get_department_2_domain(rd_list=rd_list)
        return {'domain': domain}

    @api.constrains('department' ,'department_2')
    def _constraint_department(self):
        for rec in self:
            versions = self.env['dtdream_rd_version'].search([('proName', '=', rec.id)])
            for version in versions:
                version.write({'department': rec.department.id,  'department_2': rec.department_2.id})

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
        self.write({'is_lixiangappred': False})
        self.write({'is_appred': False})
        self.write({'is_finsished_01': False, 'is_finsished_02': False})
        processes = self.env['dtdream_rd_process'].search([('process_id', '=', self.id)])
        processes.unlink()
        ztsj_processes = self.env['dtdream_rd_process'].search([('ztsj_process_id', '=', self.id)])
        ztsj_processes.unlink()
        if self.state=="state_02":
            self._wkf_message_post(statechange=u'产品状态: 总体设计->立项')
        elif self.state=='state_06':
            self._wkf_message_post(statechange=u'产品状态: 暂停->立项')
        elif self.state=='state_07':
            self._wkf_message_post(statechange=u'产品状态: 中止->立项')
        elif self.state=='state_00':
            self._wkf_message_post(statechange=u'产品状态: 草稿->立项')
            self.write({'cg_finsh_time':datetime.now()})
        self.write({'state': 'state_01'})
        self.current_approver_user = [(5,)]

    @api.multi
    def wkf_ztsj(self):
        self.write({'is_appred': False})
        self.write({'is_finsished_02': False})
        ztsj_processes = self.env['dtdream_rd_process'].search([('ztsj_process_id', '=', self.id)])
        ztsj_processes.unlink()
        if self.state=="state_03":
            self._wkf_message_post(statechange=u'产品状态: 迭代开发->总体设计')
        elif self.state=='state_06':
            self._wkf_message_post(statechange=u'产品状态: 暂停->总体设计')
        elif self.state=='state_07':
            self._wkf_message_post(statechange=u'产品状态: 中止->总体设计')
        elif self.state=='state_01':
            self._wkf_message_post(statechange=u'产品状态: 立项->总体设计')
            self.write({'lx_finsh_time':datetime.now()})
        self.write({'state': 'state_02'})
        self.current_approver_user = [(5,)]

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
        self.current_approver_user = [(5,)]

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
        self.current_approver_user = [(5,)]

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
        self.current_approver_user = [(5,)]

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
        self.current_approver_user = [(5,)]


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
        self.current_approver_user = [(5,)]

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

        versions = self.env["dtdream_rd_version"].search([('proName', '=', self.id)])
        for version in versions:
            for role in person:
                version.write({'followers_user': [(4, role)]})

        exceptions = self.env["dtdream_execption"].search([('name', '=',self.id)])
        for exception in exceptions:
            exception.role_person = [(5,)]
            for role in person:
                exception.write({'role_person': [(4,role)]})

        replannings = self.env["dtdream.rd.replanning"].search([('proname', '=', self.id)])
        for replanning in replannings:
            replanning.role_person = [(5,)]
            for role in person:
                replanning.write({'role_person': [(4, role)]})

        suspensions = self.env["dtdream.prod.suspension"].search([('project', '=', self.id)])
        for suspension in suspensions:
            suspension.role_person = [(5,)]
            for role in person:
                suspension.write({'role_person': [(4, role)]})

        suspensions = self.env["dtdream.prod.suspension.restoration"].search([('project', '=', self.id)])
        for suspension in suspensions:
            suspension.role_person = [(5,)]
            for role in person:
                suspension.write({'role_person': [(4, role)]})

        suspensions = self.env["dtdream.prod.termination"].search([('project', '=', self.id)])
        for suspension in suspensions:
            suspension.role_person = [(5,)]
            for role in person:
                suspension.write({'role_person': [(4, role)]})

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
                    self.write({'is_appred':False})
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

    #废用字段
    reason_request = fields.Text(string="申请原因")
    agree = fields.Boolean(string="同意")
    disagree = fields.Boolean(string="不同意")
    comments = fields.Text(string="审批意见")
    is_zanting = fields.Boolean(string="标记是否申请暂停")
    is_zanting_back = fields.Boolean(string="标记是否申请恢复暂停")
    is_zhongzhi = fields.Boolean(string="标记是否申请中止")
    is_zantingtj = fields.Boolean(string="标记是否提交暂停")
    is_zanting_backtj = fields.Boolean(string="标记是否提交恢复暂停")
    is_zhongzhitj = fields.Boolean(string="标记是否提交中止")
    is_ztpage = fields.Boolean(string="标记页面是否显示")
    #废用字段



    is_zantingtjN = fields.Boolean(string="标记是否提交暂停")
    is_zanting_backtjN = fields.Boolean(string="标记是否提交恢复暂停")
    is_zhongzhitjN = fields.Boolean(string="标记是否提交中止")

    execption_id = fields.Many2one('dtdream_execption',string="待提交例外")
    execption_flag = fields.Boolean(string="标记是否存在未提交例外")

    @api.onchange('pro_PDT')
    def onchange_pro_pdt(self):
        for rec in self:
            if rec.pro_PDT:
                for con in rec.role_ids:
                    if con.cof_id.name==u"PDT经理":
                        con.person = rec.pro_PDT.person.id
                        break;



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
                        if not process.is_pass and not process.is_risk:
                            self.process_email_send(product=product,process=process,state=u"立项")
                elif product.is_zhongzhitj:
                    self.special_send_email(product=product,state=u"中止")
                elif product.is_zantingtj and not product.is_zhongzhitj:
                     self.special_send_email(product=product,state=u"暂停")
            elif product.state=="state_02":
                if product.is_appred:
                    for process in product.ztsj_process_ids:
                        if not process.is_pass and not process.is_risk:
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
        list =[]
        list.append((6,0,[]))
        for reuslt in results:
            lit = {'cof_id':reuslt.id,'person':reuslt.person.id}
            list.append((0,0,lit))
        rec.update({'role_ids': list})
        return rec

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(dtdream_prod_appr, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=False)
        if res['type'] == "form":
            rd_list = []
            try:
                rd_list = openerp.tools.config['rd_list'].split(',')
            except Exception, e:
                rd_list = []
            if len(rd_list)>0:
                dm =self._get_department_domain(rd_list=rd_list)
                dm_f =self._get_department_2_domain(rd_list=rd_list)
                for field in res['fields']:
                    if field == 'department':
                        res['fields'][field]['domain'] = dm
                    if field == 'department_2':
                        res['fields'][field]['domain'] = dm_f
        return res

    def _get_parent_id(self,menu=None):
        if len(menu.parent_id)>0:
            return self._get_parent_id(menu.parent_id)
        else:
            return menu.id
    #我提交的流程
    @api.model
    def get_apply(self):
        applies=[]
        state_list = [('state_00', '草稿'), ('state_01', '立项'), ('state_02', '总体设计'), ('state_03', '迭代开发'),
                              ('state_04', '验证发布'), ('state_06', '暂停'), ('state_07', '中止'), ('state_05', '完成')]
        state_dict = dict(state_list)
        em = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        appr = self.env['dtdream_prod_appr'].search([('state','not in',('state_06','state_07','state_05'))])
        # appr = [x for x in appr if len(x.current_approver_user) > 0 and x.YF_manager.id ==em.id]
        menu_id = self._get_menu_id()
        for app in appr:
            if len(app.current_approver_user) > 0 and app.YF_manager.id ==em.id:
                department = ''
                if app.department_2:
                    department = app.department.name + '/' + app.department_2.name
                else:
                    department = app.department.name
                deferdays = (datetime.now() - datetime.strptime(app.write_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).days
                if deferdays == 0:
                    defer = False
                else:
                    defer = True
                apply={
                    'department': department,
                    'appr': app.name,
                    'version':'',
                    'PDT': app.PDT.name or '',
                    'YF_manager':app.YF_manager.name or '',
                    'style':u'产品',
                    'state': state_dict[app.state],
                    'defer':defer,
                    'url': '/web#id=' + str(app.id) + '&view_type=form&model=' + app._name + '&menu_id=' + str(menu_id),
                    'deferdays': deferdays
                }
                applies.append(apply)
        return applies

    def _get_menu_id(self):
        act_windows = self.env['ir.actions.act_window'].sudo().search([('res_model', '=', 'dtdream_prod_appr')])
        menu = None
        for act_window in act_windows:
            action_id = 'ir.actions.act_window,' + str(act_window.id)
            menu = self.env['ir.ui.menu'].sudo().search([('action', '=', action_id)])
            if len(menu)>0:
                break
        menu_id = self._get_parent_id(menu)
        return menu_id
#待我审批流程
    @api.model
    def get_affair(self):
        affairs = []
        state_list = [('state_00', '草稿'), ('state_01', '立项'), ('state_02', '总体设计'), ('state_03', '迭代开发'),
                      ('state_04', '验证发布'), ('state_06', '暂停'), ('state_07', '中止'), ('state_05', '完成')]
        state_dict = dict(state_list)
        appr = self.env['dtdream_prod_appr'].search([('current_approver_user', '=', self.env.user.id),('state','not in',('state_06','state_07','state_05'))])
        menu_id = self._get_menu_id()
        for app in appr:
            department = ''
            if app.department_2:
                department = app.department.name + '/' + app.department_2.name
            else:
                department = app.department.name
            deferdays = (datetime.now() - datetime.strptime(app.write_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).days
            if deferdays == 0:
                defer = False
            else:
                defer = True
            affair = {
                'department':department,
                'appr': app.name,
                'version': '',
                'PDT': app.PDT.name or '',
                'YF_manager': app.YF_manager.name or '',
                'style':u'产品',
                'state': state_dict[app.state],
                'defer': defer,
                'url': '/web#id=' + str(app.id) + '&view_type=form&model=' + app._name + '&menu_id=' + str(menu_id),
                'deferdays': deferdays
            }
            affairs.append(affair)
        return affairs

    @api.model
    def get_done(self):
        applies = []
        state_list = [('state_00', '草稿'), ('state_01', '立项'), ('state_02', '总体设计'), ('state_03', '迭代开发'),
                      ('state_04', '验证发布'), ('state_06', '暂停'), ('state_07', '中止'), ('state_05', '完成')]
        state_dict = dict(state_list)
        appr = self.env['dtdream_prod_appr'].search([('his_app_user', '=', self.env.user.id)])
        menu_id = self._get_menu_id()
        for app in appr:
            department=''
            if app.department_2:
                department = app.department.name+'/'+app.department_2.name
            else:
                department = app.department.name
            deferdays = (datetime.now() - datetime.strptime(app.write_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).days
            if deferdays == 0:
                defer = False
            else:
                defer = True
            apply = {
                'department': department,
                'appr': app.name,
                'version': '',
                'PDT': app.PDT.name or '',
                'YF_manager': app.YF_manager.name or '',
                'style':u'产品',
                'state': state_dict[app.state],
                'defer': defer,
                'url': '/web#id=' + str(app.id) + '&view_type=form&model=' + app._name + '&menu_id=' + str(menu_id),
                'deferdays': deferdays
            }
            applies.append(apply)
        return applies




