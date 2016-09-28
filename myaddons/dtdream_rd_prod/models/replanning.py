# -*- coding: utf-8 -*-
import openerp
from openerp import SUPERUSER_ID
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime
from lxml import etree

class dtdream_rd_replanning(models.Model):
    _name = 'dtdream.rd.replanning'
    _inherit = ['mail.thread']
    _description = u"版本重计划"

    @api.model
    def _compute_name(self):
        for rec in self:
            rec.name=rec.proname.name+u'/'+rec.version.version_numb

    name = fields.Char(compute=_compute_name,stroe=True,)
    proname = fields.Many2one('dtdream_prod_appr',string="产品", readonly=True)
    version = fields.Many2one('dtdream_rd_version',string="版本", readonly=True)
    old_plan_time = fields.Date(string="原计划发布时间",readonly=True)
    new_plan_time = fields.Date(string="重计划发布时间",required=True)
    shenpi_date = fields.Date(string="审批通过时间")
    state = fields.Selection([('state_01','草稿'),('state_02','审批中'),('state_03','已审批')],string="状态",default='state_01')
    reason = fields.Text(string="重计划原因")

    role_person = fields.Many2many("res.users" ,"dtdream_replanning_role_user",string="对应产品角色中的人员用户")

    @api.constrains('proname')
    def con_name_role(self):
        self.role_person=[(5,)]
        for role in self.proname.role_ids:
            if role.person:
                self.write({'role_person': [(4,role.person.user_id.id)]})
                if role.person.user_id:
                    self.message_subscribe_users(user_ids=[role.person.user_id.id])

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

    current_approver_user = fields.Many2one("res.users",string="当前审批人用户")

    @api.model
    def _compute_is_shenpiren(self):
        if self.env.user in self.current_approver_user:
            self.is_shenpiren=True
        else:
            self.is_shenpiren = False
    is_shenpiren = fields.Boolean(string="是否审批人",compute=_compute_is_shenpiren,readonly=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_rd_replanning, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name == u"版本重计划":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    #下方备注
    def _message_post(self,replanning,current_product,current_version,state):
        current_version.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                   <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                   <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                   <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                   <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                   </table>""" %(current_product.name,current_version.version_numb,u'提交',u'草稿->审批中'))

    @api.multi
    def btn_replanning_tj(self):
        if not self.reason:
            raise ValidationError(u"原因未填写")
        if not self.proname.department.manager_id.id:
            raise ValidationError(u"部门主管未配置")
        else:
            self.write({'current_approver_user': self.proname.department.manager_id.id})
            self.signal_workflow("cg_to_spz")

            next_shenpi = self.proname.department.manager_id
            current_product =self.proname
            current_version = self.version
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream.rd.replanning' % self.id
            url = base_url+link
            department_2=u'的'
        if current_product.department_2:
            department_2 = u"/"+current_product.department_2.name+u"的"
        subject=current_product.department.name+department_2+current_product.name+u"的"+current_version.version_numb+u"版本，提交了重计划，待您审批"
        appellation = next_shenpi.name+u",您好"
        content = current_product.department.name+u"的"+current_product.name+u"的"+current_version.version_numb+u"版本已提交了重计划，等待您的审批"
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,current_product.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % next_shenpi.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                   <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                   <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                   <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                   <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                   </table>""" %(current_product.name,current_version.version_numb,u'提交',u'草稿->审批中'))

    @api.model
    def wkf_cg(self):
        self.write({'state':'state_01'})

    @api.model
    def wkf_spz(self):
        self.write({'state':'state_02'})

    @api.model
    def wkf_ysp(self):
        self.write({'state':'state_03'})



class dtdream_rd_replanning_wizard(models.TransientModel):
    _name = 'dtdream.rd.replanning.wizard'

    @api.model
    def _compute_name(self):
        for rec in self:
            rec.name=rec.proname.name+u'/'+rec.version.version_numb

    name = fields.Char(compute=_compute_name,stroe=True,)
    proname = fields.Many2one('dtdream_prod_appr',string="产品", readonly=True)
    version = fields.Many2one('dtdream_rd_version',string="版本", readonly=True)
    old_plan_time = fields.Date(string="原计划发布时间",readonly=True)
    new_plan_time = fields.Date(string="重计划发布时间",required=True)
    shenpi_date = fields.Date(string="审批通过时间")
    state = fields.Selection([('state_01','草稿'),('state_02','审批中'),('state_03','已审批')],string="状态",default='state_01')
    reason = fields.Text(string="重计划原因")

    @api.one
    def _compute_create(self):
        if self.create_uid==self.env.user:
            self.is_create=True
        else:
            self.is_create=False
    is_create = fields.Boolean(string="是否创建者",compute=_compute_create,stroe=True,default=True)

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

    current_approver_user = fields.Many2one("res.users",string="当前审批人用户")

    @api.one
    def _compute_is_shenpiren(self):
        if self.env.user in self.current_approver_user:
            self.is_shenpiren=True
        else:
            self.is_shenpiren = False
    is_shenpiren = fields.Boolean(string="是否审批人",compute=_compute_is_shenpiren,readonly=True)


    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    #下方备注
    def _message_post(self,replanning,current_product,current_version):
        replanning.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                   <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                   <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                   <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                   <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                   </table>""" %(current_product.name,current_version.version_numb,u'提交',u'草稿->审批中'))

    @api.multi
    def btn_replanning_tj(self):
        if not self.reason:
            raise ValidationError(u"原因未填写")
        if not self.proname.department.manager_id.id:
            raise ValidationError(u"部门主管未配置")
        else:
            res = self.env['dtdream.rd.replanning'].create({'proname':self.proname.id,'version':self.version.id,'old_plan_time':self.old_plan_time,'new_plan_time':self.new_plan_time,'reason':self.reason,'state':self.state})
            res.write({'current_approver_user': self.proname.department.manager_id.id})
            res.signal_workflow("cg_to_spz")

            next_shenpi = self.proname.department.manager_id
            current_product =self.proname
            current_version = self.version
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream.rd.replanning' % res.id
            url = base_url+link
            department_2=u'的'
        if current_product.department_2:
            department_2 = u"/"+current_product.department_2.name+u"的"
        subject=current_product.department.name+department_2+current_product.name+u"的"+current_version.version_numb+u"版本，提交了重计划，待您审批"
        appellation = next_shenpi.name+u",您好"
        content = current_product.department.name+u"的"+current_product.name+u"的"+current_version.version_numb+u"版本已提交了重计划，等待您的审批"
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,current_product.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % next_shenpi.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()
        self._message_post(replanning=res,current_product=current_product,current_version=current_version)





class dtdream_rd_replanning_shenpi_wizard(models.TransientModel):
    _name = 'dtdream.rd.replanning.shenpi.wizard'

    reason= fields.Text(string="原因")

    #下方备注
    def _message_post(self,replanning,current_product,current_version,state):
        reason=self.reason or u'无'
        replanning.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                   <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                   <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                   <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                   <tr><td style="padding:10px">原因</td><td style="padding:10px">%s</td></tr>
                                   <tr><td style="padding:10px">状态变化</td><td style="padding:10px">%s</td></tr>
                                   </table>""" %(current_product.name,current_version.version_numb,u'审批',reason,state))
        replanning.current_approver_user=False

    @api.one
    def btn_agree(self):
        replanning = self.env['dtdream.rd.replanning'].browse(self._context['active_id'])
        replanning.signal_workflow("spz_to_ysp")
        self._message_post(replanning=replanning,current_product=replanning.proname,current_version=replanning.version,state=u'审批中->已审批')
        replanning.write({'shenpi_date':datetime.now()})

    @api.one
    def btn_disagree(self):
        if not self.reason:
            raise ValidationError(u'请填写原因')
        else:
             replanning = self.env['dtdream.rd.replanning'].browse(self._context['active_id'])
             replanning.signal_workflow("spz_to_cg")
             self._message_post(replanning=replanning,current_product=replanning.proname,current_version=replanning.version,state=u'审批中->草稿')
