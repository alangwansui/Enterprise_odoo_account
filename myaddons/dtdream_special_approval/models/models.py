# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from lxml import etree
from dateutil.relativedelta import relativedelta
#专项主表
class dtdream_special_approval(models.Model):
    _name = 'dtdream.special.approval'
    _inherit = ['mail.thread']
    _description = u"专项审批"

    name = fields.Char(string='编码',copy=False,readonly=True)
    applicant = fields.Many2one("hr.employee",string="申请人",required=True,store=True,default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]),readonly=True,stroe=True)

    @api.depends('applicant')
    def _compute_employee(self):
        for rec in self:
            rec.job_number=rec.applicant.job_number
            rec.department=rec.applicant.department_id
            rec.mobile_phone = rec.applicant.mobile_phone
            rec.sq_depart_number = rec.applicant.department_id.code

    job_number = fields.Char(compute=_compute_employee,string="工号")
    department = fields.Many2one("hr.department",compute=_compute_employee,string="申请部门" ,store=True)
    sq_depart_number=fields.Char(compute=_compute_employee,string="申请部门编码" ,store=True)
    department_sy = fields.Many2one("hr.department",string="受益部门",required=True,default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]).department_id)
    sy_depart_number=fields.Char(compute=_compute_employee,string="受益部门编码" ,store=True)
    mobile_phone = fields.Char(compute=_compute_employee,string="联系电话")
    business_type = fields.Selection([('type1','公司/样板点考察类'),('type2','品牌/解决方案类'),('type3','渠道扩展类'),('type4','行政事务类')],string='业务类型',required=True)
    business_item = fields.Char(string="业务事项",required=True)
    event_location = fields.Char(string="活动地点",required=True)
    customer_unit = fields.Many2one('res.partner',string="客户单位",required=True)
    activities_desc = fields.Text(string="专项活动必要性描述",required=True)
    state = fields.Selection([('state_01','草稿'),('state_02','主管审批'),('state_03','权签人审批'),('state_04','财务审批'),('state_05','完成')],string="状态",default='state_01')
    product = fields.Many2one('crm.lead',string="项目")

    detail_ids = fields.One2many("dtdream.events.agenda","approval","专项活动议程简述")
    fee_ids = fields.One2many("dtdream.approval.fee","fee","费用详情")

    current_approver_user = fields.Many2one("res.users",string="当前审批人用户")

    @api.onchange("department_sy")
    def _onchang_department_sy(self):
        for rec in self :
            rec.sy_depart_number=rec.department_sy.code

    @api.depends("current_approver_user")
    def _depends_user(self):
        for rec in self :
            em = self.env['hr.employee'].search([('user_id','=',rec.current_approver_user.id)])
            rec.current_approver=em.id
    current_approver = fields.Many2one("hr.employee",compute="_depends_user",string="当前审批人")

    #流程流向审批人
    shenpi_zer = fields.Many2one("hr.employee",string="部门审批人")
    shenpi_zer_shouyi = fields.Many2one("hr.employee",string="受益部门审批人")
    shenpi_fir = fields.Many2one("hr.employee",string="权签一审批人")
    shenpi_sec = fields.Many2one("hr.employee",string="权签二审批人")
    shenpi_thr = fields.Many2one("hr.employee",string="权签三审批人")
    shenpi_fou = fields.Many2one("hr.employee",string="最终审批人")
    shenpi_fif = fields.Many2one("hr.employee",string="财务审批人")
    shenpi_six = fields.Many2one("hr.employee",string="财务最终审批人")
    deadline = fields.Char(string="审批截至时间")

    help_state = fields.Selection([('department_01','部门审批'),('department_02','受益部门审批'),('quanqian_01','第一权签'),('quanqian_02','第二权签'),('quanqian_03','第三权签'),('quanqian_04','最终审批'),('cw_01','第一财务权签'),('cw_02','最终财务权签')],string="详细状态")

    @api.model
    def _compute_create(self):
        if self.create_uid==self.env.user:
            self.is_create=True
        else:
            self.is_create=False
    is_create = fields.Boolean(string="是否创建者",compute=_compute_create,stroe=True,default=True)

    @api.model
    def _compute_is_shenpiren(self):
        if self.env.user in self.current_approver_user:
            self.is_shenpiren=True
        else:
            self.is_shenpiren = False
    is_shenpiren = fields.Boolean(string="是否审批人",compute=_compute_is_shenpiren,readonly=True)

    @api.model
    def _compute_is_manager(self):
        users =  self.env.ref("dtdream_special_approval.group_dtdream_special_approval_manager").users
        if self.env.user in users:
            self.is_manager = True
        else:
            self.is_manager=False
    is_manager = fields.Boolean(string="是否在管理组",compute=_compute_is_manager,readonly=True)

    @api.depends('fee_ids')
    def _onchange_fee(self):
        total=0
        for rec in self.fee_ids:
            total+=rec.money
        self.total = total
    total = fields.Integer(string="合计(元)",store=True,compute=_onchange_fee)

    @api.constrains('message_follower_ids')
    def _compute_follower(self):
        self.followers_user = False
        for foll in self.message_follower_ids:
            self.write({'followers_user': [(4,foll.partner_id.user_ids.id)]})

    followers_user = fields.Many2many("res.users" ,"dtdream_special_approval_f",string="关注者")

    his_approver_user = fields.Many2many("res.users" ,"dtdream_special_approval_his",string="历史审批人员")


    #判断上级部门是否有权签路径
    @api.multi
    def _com_department(self,department=None):
        if department.parent_id:
            if department.parent_id.zxfirst_person:
                return True
            else:
                self._com_department(department=department.parent_id)
        else:
            return False

    #判断上级部门是否有权签路径,存在及取部门
    @api.multi
    def _com_department_info(self,department=None):
        if department.parent_id:
            if department.parent_id.zxfirst_person:
                return department.parent_id
            else:
                self._com_department_info(department=department.parent_id)
        else:
            return False


#操作动作
#草稿提交

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    def add_follower(self, cr, uid, ids, employee_id, context=None):
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
        if employee and employee.user_id:
            self.message_subscribe_users(cr, uid, ids, user_ids=[employee.user_id.id], context=context)

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

    @api.multi
    def _send_email(self,next_approver):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.special.approval' % self.id
        url = base_url+link
        appellation = next_approver.name+u",您好"
        subject=self.applicant.name+u"提交的编号为‘"+self.name+u"’的专项审批，等待您的审批"
        content = self.applicant.name+u"提交的编号为‘"+self.name+u"’的专项审批，等待您的审批"
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
        # self.add_follower(employee_id=current_approver.id)

    @api.multi
    def _message_poss(self,statechange,action,next_shenpiren=None):
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">专项编号</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">下阶段审批人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" %(self.name,statechange,action,next_shenpiren))

    @api.multi
    def do_cgtj(self):
        list=['type1']
        if self.business_type in list and not self.product:
            raise ValidationError(u'当业务类型为"公司/样板点考察类",项目必填')
        if len(self.detail_ids)<1:
            raise ValidationError(u'专项活动议程简述必须有一条')
        if self.total<=0:
            raise ValidationError(u'合计金额必须大于0')
        if not self.applicant.department_id.manager_id:
            raise ValidationError(u"请配置本部门主管信息")
        if not self.department_sy.manager_id:
            raise ValidationError(u"请配置受益部门主管信息")
        if not self.department_sy.zxfirst_person and not self._com_department(department=self.department_sy):
            raise ValidationError(u'请配置一级审批人')
        self.write({'deadline':datetime.now() + relativedelta(days=2)})
        specificlist = self.env['dtdream.specific.people'].search([])
        specific=''
        if len(specificlist)>0:
            specific=specificlist[0]
        if not specific:
            raise ValidationError(u'请配置特定权签人')
        if self.department_sy.zxfirst_person:#走受益部门的权签路径
            department_sy = self.department_sy
            if specific.cw_quanqian:
                self.write({'shenpi_zer':self.applicant.department_id.manager_id.id,'shenpi_zer_shouyi':department_sy.manager_id.id,'shenpi_fir': department_sy.zxfirst_person.id,'shenpi_fif':specific.cw_quanqian.id})
            else:
                self.write({'shenpi_zer':self.applicant.department_id.manager_id.id,'shenpi_zer_shouyi':department_sy.manager_id.id,'shenpi_fir': department_sy.zxfirst_person.id,'shenpi_six':specific.last_quanqian.id})
            if self.applicant.department_id.manager_id==department_sy.manager_id:
                self.write({'shenpi_zer_shouyi':False})
            if self.total>department_sy.zxfirst_money:
                if department_sy.zxsec_person:
                    self.write({'shenpi_sec':department_sy.zxsec_person.id})
                    if self.total>department_sy.zxsec_money:
                        if department_sy.zxthird_person:
                            self.write({'shenpi_thr':department_sy.zxthird_person.id})
                            if self.total>department_sy.zxthird_money:
                                self.write({'shenpi_fou':specific.last_shenpi.id})
                            if self.applicant==department_sy.zxthird_person:
                                self.write({'shenpi_zer':False,'shenpi_zer_shouyi':False,'shenpi_fir':False,'shenpi_sec':False,'shenpi_thr':False})
                        else:
                            self.write({'shenpi_fou':specific.last_shenpi.id})
                    if self.applicant==department_sy.zxsec_person:
                        self.write({'shenpi_zer':False,'shenpi_zer_shouyi':False,'shenpi_fir':False,'shenpi_sec':False})
                else:
                    self.write({'shenpi_fou': specific.last_shenpi.id})
            if self.applicant == self.applicant.department_id.manager_id:
                self.write({'shenpi_zer':False})
            if self.applicant ==department_sy.manager_id:
                self.write({'shenpi_zer':False,'shenpi_zer_shouyi':False})
            if self.applicant == department_sy.zxfirst_person:
                self.write({'shenpi_zer':False,'shenpi_zer_shouyi':False,'shenpi_fir':False})
            if department_sy.manager_id==department_sy.zxfirst_person:
                self.shenpi_fir=False
            if specific.cw_quanqian and self.total>specific.money:
                self.write({'shenpi_six': specific.last_quanqian.id})
                if specific.cw_quanqian==specific.last_quanqian:
                    self.shenpi_fif=False

        elif self._com_department(department=self.department_sy):#走受益部门上级部门的权签路径
            pardepartment =self._com_department_info(department=self.department_sy)
            if specific.cw_quanqian:
                self.write({'shenpi_zer':self.applicant.department_id.manager_id.id,'shenpi_zer_shouyi':self.department_sy.manager_id.id,'shenpi_fir': pardepartment.zxfirst_person.id,'shenpi_fif':specific.cw_quanqian.id})
            else:
                self.write({'shenpi_zer':self.applicant.department_id.manager_id.id,'shenpi_zer_shouyi':self.department_sy.manager_id.id,'shenpi_fir': pardepartment.zxfirst_person.id,'shenpi_six':specific.last_quanqian.id})
            if self.applicant.department_id==self.department_sy:
                self.write({'shenpi_zer_shouyi':False})
            if self.total>pardepartment.zxfirst_money:
                if pardepartment.zxsec_person:
                    self.write({'shenpi_sec':pardepartment.zxsec_person.id})
                    if self.total>pardepartment.zxsec_money:
                        if pardepartment.zxthird_person:
                            self.write({'shenpi_thr':pardepartment.zxthird_person.id})
                            if self.total>pardepartment.zxthird_money:
                                self.write({'shenpi_fou':specific.last_shenpi.id})
                            if self.applicant==pardepartment.zxthird_person:
                                self.write({'shenpi_zer':False,'shenpi_zer_shouyi':False,'shenpi_fir':False,'shenpi_sec':False,'shenpi_thr':False})
                        else:
                            self.write({'shenpi_fou':specific.last_shenpi.id})
                    if self.applicant==pardepartment.zxsec_person:
                        self.write({'shenpi_zer':False,'shenpi_zer_shouyi':False,'shenpi_fir':False,'shenpi_sec':False})
                else:
                    self.write({'shenpi_fou': specific.last_shenpi.id})
            if self.applicant ==self.applicant.department_id.manager_id:
                self.shenpi_zer=False
            if self.applicant ==self.department_sy.manager_id:
                self.write({'shenpi_zer':False,'shenpi_zer_shouyi':False})
            if self.applicant == pardepartment.zxfirst_person:
                self.write({'shenpi_zer':False,'shenpi_zer_shouyi':False,'shenpi_fir':False})
            if self.department_sy.manager_id==pardepartment.zxfirst_person:
                self.shenpi_fir=False
            if specific.cw_quanqian and self.total>specific.money:
                self.write({'shenpi_six': specific.last_quanqian.id})
                if specific.cw_quanqian==specific.last_quanqian:
                    self.shenpi_fif=False

        if self.shenpi_zer or self.shenpi_zer_shouyi:
            self.signal_workflow('cg_to_zgsp')
            if self.shenpi_zer:
                self.write({'current_approver_user': self.shenpi_zer.user_id.id,'help_state':'department_01'})
                self._message_poss(statechange=u'草稿->主管审批',action=u'提交',next_shenpiren=self.shenpi_zer.name)
                self._send_email(next_approver=self.shenpi_zer)
            elif self.shenpi_zer_shouyi:
                self.write({'current_approver_user': self.shenpi_zer_shouyi.user_id.id,'help_state':'department_02'})
                self._message_poss(statechange=u'草稿->主管审批',action=u'提交',next_shenpiren=self.shenpi_zer_shouyi.name)
                self._send_email(next_approver=self.shenpi_zer_shouyi)
        elif self.shenpi_fir or self.shenpi_sec or self.shenpi_thr or self.shenpi_fou:
            self.signal_workflow('cg_to_qqrsp')
            if self.shenpi_fir:
                self._message_poss(statechange=u'草稿->权签人审批',action=u'提交',next_shenpiren=self.shenpi_fir.name)
                self.write({'current_approver_user': self.shenpi_fir.user_id.id,'help_state':'quanqian_01'})
                self._send_email(next_approver=self.shenpi_fir)
            elif self.shenpi_sec:
                self._message_poss(statechange=u'草稿->权签人审批',action=u'提交',next_shenpiren=self.shenpi_sec.name)
                self.write({'current_approver_user': self.shenpi_sec.user_id.id,'help_state':'quanqian_02'})
                self._send_email(next_approver=self.shenpi_sec)
            elif self.shenpi_thr:
                self._message_poss(statechange=u'草稿->权签人审批',action=u'提交',next_shenpiren=self.shenpi_thr.name)
                self.write({'current_approver_user': self.shenpi_thr.user_id.id,'help_state':'quanqian_03'})
                self._send_email(next_approver=self.shenpi_thr)
            elif self.shenpi_fou:
                self._message_poss(statechange=u'草稿->权签人审批',action=u'提交',next_shenpiren=self.shenpi_fou.name)
                self.write({'current_approver_user': self.shenpi_fou.user_id.id,'help_state':'quanqian_04'})
                self._send_email(next_approver=self.shenpi_fou)
        elif self.shenpi_fif or self.shenpi_six:
            self.signal_workflow('cg_to_cwsp')
            if self.shenpi_fif:
                self._message_poss(statechange=u'草稿->财务审批',action=u'提交',next_shenpiren=self.shenpi_fif.name)
                self.write({'current_approver_user': self.shenpi_fif.user_id.id,'help_state':'cw_01'})
                self._send_email(next_approver=self.shenpi_fif)
            elif self.shenpi_six:
                self._message_poss(statechange=u'草稿->财务审批',action=u'提交',next_shenpiren=self.shenpi_six.name)
                self.write({'current_approver_user': self.shenpi_six.user_id.id,'help_state':'cw_02'})
                self._send_email(next_approver=self.shenpi_six)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            em = self.env["hr.employee"].search([("user_id", "=", self.env.user.id)])
            num = 1
            approvs= self.search([('create_date','like',(datetime.now().strftime('%Y-%m-%d')+"%"))], order="id desc")
            if len(approvs)>0:
                num = int(approvs[0].name[-3:])+1
            if num < 100:
                num = "%03d"%num
            vals['name'] = ''.join(['ZX',datetime.now().strftime('%Y%m%d'),num]) or 'New'
        result = super(dtdream_special_approval, self).create(vals)
        return result

#流程方法
    @api.model
    def wkf_cg(self):
        self.write({'state':'state_01'})

    @api.model
    def wkf_zgsp(self):
        self.write({'state':'state_02'})

    @api.model
    def wkf_qqrsp(self):
        self.write({'state':'state_03'})

    @api.model
    def wkf_cwsp(self):
        self.write({'state':'state_04'})

    @api.model
    def wkf_wc(self):
        self.write({'state':'state_05'})

    @api.model
    def timing_send_email(self):
        applications=self.env['dtdream.special.approval'].sudo().search([('state','in',('state_02','state_03','state_04')),('deadline','<',datetime.now())])
        for application in applications:
            em = self.env['hr.employee'].search([('user_id','=',application.current_approver_user.id)])
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream.special.approval' % application.id
            url = base_url+link
            appellation = em.name+u",您好"
            subject=application.applicant.name+u"提交的编号为‘"+application.name+u"’的专项审批，等待您的审批"
            content = application.applicant.name+u"提交的编号为‘"+application.name+u"’的专项审批，您尚未审批请及时处理"
            self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                             <p>%s</p>
                             <p> 请点击链接进入:
                             <a href="%s">%s</a></p>
                            <p>dodo</p>
                             <p>万千业务，简单有do</p>
                             <p>%s</p>''' % (appellation,content, url,url,application.write_date[:10]),
                'subject': '%s' % subject,
                'email_to': '%s' % em.work_email,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()


#具体事宜
class dtdream_events_agenda(models.Model):
    _name = "dtdream.events.agenda"
    name=fields.Char()

    date = fields.Date(string="年月日",required=True)
    period = fields.Selection([('period1','上午'),('period2','下午'),('period3','晚上')],string="时间段")
    place = fields.Char(string="地点/场所",required=True)
    issues = fields.Char(string="行程/议题",required=True)
    clients = fields.Integer(string="客户人数",required=True)
    accompany_num = fields.Integer(string="内部陪同人数",required=True)
    remark = fields.Char(string="备注")

    approval = fields.Many2one("dtdream_special_approval",ondelete="cascade")

#费用详情
class dtdream_approval_fee(models.Model):
    _name = "dtdream.approval.fee"
    name=fields.Char()
    fee_type = fields.Selection([('fee_type1','餐费(含酒水)'),('fee_type2','会务场租'),('fee_type3','住宿费'),('fee_type4','交通费用'),('fee_type5','礼品费用'),('fee_type6','其他')],string="费用类别",required=True)
    money =fields.Integer(string="金额(元)",required=True)
    remark = fields.Char(string="费用事项说明",required=True)
    fee= fields.Many2one("dtdream_special_approval",ondelete="cascade")

#部门权签人设置
class dtdream_approval_right_peo(models.Model):
    _inherit = 'hr.department'
    name=fields.Char()
    zxfirst_person=fields.Many2one("hr.employee",string="第一权签人")
    zxsec_person=fields.Many2one("hr.employee",string="第二权签人")
    zxthird_person=fields.Many2one("hr.employee",string="第三权签人")
    # fouth_person=fields.Many2one("hr.employee",string="第四审批人")
    zxfirst_money=fields.Integer(string="第一权签人金额(元)")
    zxsec_money=fields.Integer(string="第二权签人金额(元)")
    zxthird_money=fields.Integer(string="第三权签人金额(元)")
    # fouth_money=fields.Integer(string="第四审批人金额")

    @api.constrains('zxfirst_person','zxfirst_money')
    def _con_zxfirst_person(self):
        if self.zxfirst_person:
            if not self.zxfirst_money or self.zxfirst_money<=0 :
                raise ValidationError(u'设置了权签人，则必须设置对应的金额')
            elif self.zxsec_money>0 and self.zxfirst_money>=self.zxsec_money:
                raise ValidationError(u'一级权签金额不应大于二级')

    @api.constrains('zxsec_person','zxsec_money')
    def _con_zxsec_person(self):
        if self.zxsec_person:
            if not self.zxfirst_person:
                raise ValidationError(u'请按顺序设置权签人')
            if not self.zxsec_money or self.zxsec_money<=0:
                raise ValidationError(u'设置了权签人，则必须设置对应的金额')
            elif self.zxfirst_money>=self.zxsec_money:
                raise ValidationError(u'二级权签金额不应小于一级')
            elif self.zxthird_money>0 and self.zxthird_money<=self.zxsec_money:
                raise ValidationError(u'二级权签金额不应大于三级')


    @api.constrains('zxthird_person','zxthird_money')
    def _con_zxthird_person(self):
        if self.zxthird_person:
            if not self.zxfirst_person or not self.zxsec_person:
                raise ValidationError(u'请按顺序设置权签人')
            if not self.zxthird_money or self.zxthird_money<=0:
                raise ValidationError(u'设置了权签人，则必须设置对应的金额')
            elif self.zxfirst_money>=self.zxthird_money:
                raise ValidationError(u'三级权签金额不应小于一级')
            elif self.zxthird_money<=self.zxsec_money:
                raise ValidationError(u'三级权签金额不应小于二级')

#特殊权签设置
class dtdream_specific_people(models.Model):
    _name = 'dtdream.specific.people'
    name =fields.Char(default="特定权签设置")
    last_shenpi = fields.Many2one("hr.employee",string="最终审批人",required=True)
    cw_quanqian = fields.Many2one("hr.employee",string="财务权签人")
    money= fields.Integer(string="财务权签金额")
    last_quanqian = fields.Many2one("hr.employee",string="财务最终权签人",required=True)

    @api.constrains('cw_quanqian','money')
    def _con_cw_quanqian(self):
        if self.cw_quanqian:
            if not self.money or self.money<=0:
                raise ValidationError(u'设置了权签人，则必须设置对应的金额')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        cr = self.env["dtdream.specific.people"].search([])
        res = super(dtdream_specific_people, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        if res['type'] == "form":
            if cr:
                doc = etree.XML(res['arch'])
                doc.xpath("//form")[0].set("create", "false")
                res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def create(self, vals):
        specificlist = self.env['dtdream.specific.people'].search([])
        if len(specificlist)>0:
            raise ValidationError(u'特定权签人已创建')
        result = super(dtdream_specific_people, self).create(vals)
        self.fields_view_get()
        return result

class dtdream_special_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends("approval_ids")
    def _compute_approval_nums(self):
        cr = self.env["dtdream.special.approval"].search([("customer_unit.id", "=", self.id)])
        self.approval_nums = len(cr)

    @api.one
    def _compute_can_view(self):
        if self.user_id == self.env.user:
            self.can_view = True
        else:
            self.can_view = False
    can_view = fields.Boolean(compute="_compute_can_view")
    approval_ids = fields.One2many("dtdream.special.approval","customer_unit",string="专项")
    approval_nums = fields.Integer(compute='_compute_approval_nums', string="专项数量",stroe=True)