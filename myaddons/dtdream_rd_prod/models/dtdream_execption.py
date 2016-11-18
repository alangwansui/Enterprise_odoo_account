# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError

#例外
class dtdream_execption(models.Model):
    _name = "dtdream_execption"
    _inherit =['mail.thread']
    _description = u"例外"
    name=fields.Many2one("dtdream_prod_appr" ,required=True,string="产品名称")
    version = fields.Many2one("dtdream_rd_version",string="版本")
    reason = fields.Text(string="例外原因",track_visibility='onchange')
    state= fields.Selection([('dsp','待审批'),('yjsp','一级审批'),('Nyjsp','一级审批不通过'),('ejsp','二级审批'),('Nejsp','二级审批不通过'),('ysp','已审批')],string="状态",default='dsp')
    flag = fields.Boolean(string="标记保存取消按钮是否可见")
    mark = fields.Boolean(string="用于区分是从产品还是版本")
    is_apped = fields.Boolean(string="标记是否提交")

    approver_fir = fields.Many2one("hr.employee" ,string="第一审批人质量代表")
    approver_sec = fields.Many2one("hr.employee",string="第二审批人PL-CCB")

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
    def execptiontj(self):
        # res= self.write({'name':self.name.id,'version':self.version.id,'reason':self.reason,'state':'dsp','is_apped':True})
        if not self.reason:
            raise ValidationError(u'例外原因不能为空')
        if not self.approver_fir:
            raise ValidationError(u"第一审批人不能为空")
        if not self.version:
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
        # return res

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

    @api.depends("current_approver_user")
    def _depends_user(self):
        for rec in self:
            if rec.current_approver_user:
                em = self.env['hr.employee'].search([('user_id','=',rec.current_approver_user.id)])
                rec.current_approver=em.id
            else:
                rec.current_approver=False
    current_approver = fields.Many2one("hr.employee",compute="_depends_user",string="当前经办人")


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
    is_create = fields.Boolean(string="是否创建者",compute=_compute_create,default=True)

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

    @api.onchange('message_follower_ids')
    def _compute_follower(self):
        self.followers_user = False
        for foll in self.message_follower_ids:
            self.write({'followers_user': [(4,foll.partner_id.user_ids.id)]})
            if foll.partner_id.user_ids not in self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users:
                self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").sudo().write({'users': [(4,foll.partner_id.user_ids.id)]})

    followers_user = fields.Many2many("res.users" ,"execption_f_u_u",string="关注者")

    @api.constrains('name')
    def con_name_role(self):
        self.role_person=[(5,)]
        for role in self.name.role_ids:
            if role.person:
                self.write({'role_person': [(4,role.person.user_id.id)]})
                if role.person.user_id:
                    self.message_subscribe_users(user_ids=[role.person.user_id.id])