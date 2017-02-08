# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from openerp.osv.orm import setup_modifiers
from dateutil.relativedelta import relativedelta
from datetime import datetime,time

import time
from lxml import etree

from openerp.exceptions import ValidationError

try:
    import xlwt
except ImportError:
    xlwt = None


class dtdream_contract_url(models.Model):
    _name = "dtdream.contract.url"

    name = fields.Char(string="标准合同下载地址")


class dtdream_contract(models.Model):
    _name = 'dtdream.contract'
    _inherit = ['mail.thread']
    _description = u'合同评审'

    his_approve = fields.Many2many('hr.employee',string="历史审批人")
    name = fields.Char(string="合同名称")

    def get_contract_id(self):
        #    计算合同编号
        max_contract_id = ''
        name_id = self.contract_subtype.name_id or self.contract_type.name_id
        if name_id:
            baseid = 'HZSM-' + name_id + '-' + time.strftime("%Y%m", time.localtime())
            sql_baseid = baseid + "%"
            self._cr.execute("select contract_id from dtdream_contract where contract_id like '"+sql_baseid+"' order by contract_id desc limit 1")
            for rec in self._cr.fetchall():
                max_contract_id = rec[0]
            if max_contract_id:
                max_id = max_contract_id[-4:]
                return (baseid + '%04d' % (int(max_id)+1))
            else:
                return (baseid + '0001')

    def get_approvers(self):
        # 获取审批人
        config = False
        if self.contract_type.how_setting_approver == 'type':
            config = self.contract_type
        elif self.contract_type.how_setting_approver == 'subtype':
            config = self.contract_subtype
        if config:
            self.legal_interface = config.legal_interface
            self.review_ids = config.review_ids
            self.huiqian_ids = config.huiqian_ids
            self.quanqian_id = config.quanqian_id
            self.stamp_id = config.stamp_id
            self.file_id = config.file_id

    @api.onchange('contract_subtype')
    def compute_contract_id_and_approver_when_subtype_change(self):
        if self.contract_subtype:
            if self.contract_type != self.contract_subtype.parent_id:
                self.contract_type = self.contract_subtype.parent_id.id
        self.contract_id = self.get_contract_id()
        self.contract_id_copy = self.get_contract_id()
        self.get_approvers()

    @api.onchange('contract_type')
    def get_contract_subtype_domain(self):
        if self.contract_type:
            if self.contract_subtype.parent_id != self.contract_type:
                self.contract_subtype = False
            return {
                'domain': {
                    "contract_subtype": [('parent_id', '=', self.contract_type.id)]
                }
            }
        elif not self.contract_type:
            return {
                'domain': {
                    "contract_subtype": [('parent_id', '!=', False)]
                }
            }

    @api.onchange('contract_type')
    def compute_contract_id_and_approver_when_type_change(self):
        if self.contract_type:
            if self.contract_subtype.parent_id != self.contract_type:
                self.contract_subtype = False
        self.contract_id = self.get_contract_id()
        self.contract_id_copy = self.get_contract_id()
        self.get_approvers()

    @api.constrains('contract_type','contract_subtype')
    def save_readonly_contract_id_and_approver(self):
        self.contract_id = self.contract_id_copy
        self.get_approvers()

    contract_id = fields.Char(string="合同编号", store=True)
    if_must_subtype = fields.Boolean(string='是否必须选择合同子类型')

    @api.onchange('contract_type')
    def compute_if_must_subtype(self):
        self.if_must_subtype = False
        if self.contract_type.how_setting_approver == 'subtype':
            self.if_must_subtype = True

    contract_type = fields.Many2one("dtdream.contract.type", string="合同类型")
    contract_subtype = fields.Many2one('dtdream.contract.subtype', string='合同子类型')
    contract_id_copy = fields.Char(string="合同编号暂存")

    applicant = fields.Many2one('hr.employee',string='申请人', default=lambda self:self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]) )
    @api.one
    @api.onchange("applicant")
    def _compute_employee(self):
        self.job_number=self.applicant.job_number
        self.deparment=self.applicant.department_id.complete_name
        self.tel_number=self.applicant.mobile_phone
        self.deparment_manage=self.applicant.department_id.manager_id.id
    # job_number=fields.Char(string="工号",compute=_compute_employee)
    def _compute_is_applicant(self):
        # 判断是否是申请人或者创建人
        if self.state:
            if self.env.user.id != self.applicant.user_id.id and self.env.user.id != self.create_uid.id:
                self.is_applicant=False
            else:
                self.is_applicant=True
        else:
            self.is_applicant=True
        #     判断是否是主管
        if self.env.user.id != self.deparment_manage.user_id.id:
            self.is_manager=False
        else:
            self.is_manager=True
        #判断是否是归档人
        if self.env.user.id != self.file_id.user_id.id:
            self.is_file_id = False
        else:
            self.is_file_id = True


    is_applicant=fields.Boolean(string="是否申请人或创建人",compute=_compute_is_applicant,default=True)
    is_manager=fields.Boolean(string="是否是主管",compute=_compute_is_applicant)
    job_number=fields.Char(string="工号",compute=_compute_employee)
    deparment=fields.Char(string="部门",compute=_compute_employee)
    tel_number=fields.Char(string="电话",compute=_compute_employee)
    deparment_manage=fields.Many2one('hr.employee',string="部门主管")
    state=fields.Selection([("0", "草稿"), ("1", "主管审批"), ("2", "待组织评审"),("3","评审中"),("4","待组织会签"),("5","会签中"),("6","权签中"),("7","待盖章"),("8","待归档"),("9","闭环"),("10","作废")],string="合同状态")
    create_time=fields.Datetime(string='创建时间',default=lambda self:datetime.now(),readonly=1)
    money=fields.Float(string="合同金额(元)")
    background=fields.Text(string="合同背景介绍")
    items = fields.Char(string='付款条款')
    deadline = fields.Char(string='合同期限')
    risk_warning = fields.Char(string='风险提示')
    amounts = fields.Integer(string='合同份数')
    stamp_type = fields.Selection([('1','公章'),('2','合同专用章'),('3','法人章')],string='印章类型')
    attachment_ids = fields.One2many('dtdream.contract.attachment','contract_id',string='合同附件',required=1)
    remark=fields.Char(string="备注")
    # pro_name=fields.Many2one("crm.lead",string="项目名称")
    pro_responsible_person = fields.Many2one('hr.employee',string='项目负责人')
    tip=fields.Char(default=lambda self:self.env['dtdream.contract.url'].search([],limit=1).name)
    partner_jia = fields.Many2one('res.partner',string='签约方(甲方)',domain=['|',('supplier','=',True),('customer','=',True)])
    partner_yi = fields.Many2one('res.partner',string='签约方(乙方)',domain=['|',('supplier','=',True),('customer','=',True)])
    partner_bing = fields.Many2one('res.partner',string='签约方(其他方)',domain=['|',('supplier','=',True),('customer','=',True)])
    is_standard=fields.Boolean(string="是标准合同",help='标准合同无需评审，直接进入会签环节，可快速完成合同评审流程')
    current_handler_ids=fields.Many2many('hr.employee','c_i_h_e',string="当前处理人",store=True)

    @api.one
    def _compute_is_handler(self):
        self.is_handler = False
        if self.current_handler_ids:
            for handler in self.current_handler_ids:
                if handler.user_id.id == self.env.user.id:
                    self.is_handler = True

    @api.one
    def _compute_is_legal_interface(self):
        self.is_legal_interface = False
        if self.legal_interface:
            for people in self.legal_interface:
                if people.user_id.id == self.env.user.id:
                    self.is_legal_interface = True
    is_handler=fields.Boolean("是否当前处理人",compute=_compute_is_handler)
    is_legal_interface=fields.Boolean("是否法务部接口人",compute=_compute_is_legal_interface)
    legal_interface=fields.Many2many('hr.employee','dt_contract_legal_interface',string="法务接口人")
    review_ids=fields.Many2many('hr.employee','r_i_h_e',string="评审人",store=True)
    def _compute_is_review_ids(self):
        self.is_review_ids = False
        if self.review_ids:
            for people in self.review_ids:
                if people.user_id.id == self.env.user.id:
                    self.is_review_ids = True
    is_review_ids = fields.Boolean(string='是否是评审人',compute=_compute_is_review_ids)
    huiqian_ids=fields.Many2many('hr.employee','h_i_h_e',string="会签人")
    quanqian_id=fields.Many2one('hr.employee',string="权签人")
    stamp_id=fields.Many2one('hr.employee',string="盖章处理人")

    def _compute_stamp(self):
        self.is_stamped=True
        self.stamp_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


    def _compute_file(self):
        self.is_filed=True
        self.file_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    is_stamped=fields.Boolean(string="是否已盖章")
    stamp_time=fields.Char(string="盖章时间")
    file_id=fields.Many2one('hr.employee',string="归档处理人")
    is_filed=fields.Boolean(string="是否已归档")
    is_file_id=fields.Boolean(string='是否归档人',compute=_compute_is_applicant)
    file_time=fields.Char(string="归档时间")
    review2wait_countersign=fields.Boolean(default=False)

    def send_email(self,cr,uid,id):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')

        link='/web?#id=%s&view_type=form&model=dtdream.contract'%id
        url=base_url+link
        damn_self=self.pool.get('dtdream.contract').browse(cr, uid,id)
        style1 = 'none'
        style2 = 'none'
        style3 = 'none'
        if damn_self.partner_jia:
            style1 = 'block'
        if damn_self.partner_yi:
            style2 = 'block'
        if damn_self.partner_bing:
            style3 = 'block'
        for people in damn_self.current_handler_ids:
            damn_self.env['mail.mail'].create({
                    'subject': u'%s于%s提交合同：%s-%s 评审申请，请您审批！' % (damn_self.applicant.name, damn_self.create_time[:10],damn_self.contract_type.name,damn_self.contract_subtype.name),
                    'body_html': u'''
                    <p>%s，您好：</p>
                    <p>%s提交的合同评审正等待您的审批！</p>
                    <p>合同信息如下：</p>
                    <p>合同名称：%s</p>
                    <p>合同编号：%s</p>
                    <p>合同类型：%s-%s</p>
                    <p style='display:%s'>签约方(甲方)：%s</p>
                    <p style='display:%s'>签约方(乙方)：%s</p>
                    <p style='display:%s'>签约方(其他方)：%s</p>
                    <p> 请点击链接进入审批:
                    <a href="%s">%s</a></p>
                    <p>dodo</p>
                    <p>万千业务，简单有do</p>
                    <p>%s</p>''' % (people.name, damn_self.applicant.name,damn_self.name,
                                    damn_self.contract_id,damn_self.contract_type.name,damn_self.contract_subtype.name,
                                    style1,damn_self.partner_jia,style2,damn_self.partner_yi,
                                    style3,damn_self.partner_bing, url, url, damn_self.write_date[:10]),
                    'email_from':damn_self.env['ir.mail_server'].search([], limit=1).smtp_user,
                    'email_to': people.work_email,
                }).send()
        return url

    @api.one
    def copy(self, default=None):
        default = dict(default or {}, contract_id="")
        print default
        return super(dtdream_contract, self).copy(default=default)

    @api.model
    def create(self,vals):
        result = super(dtdream_contract, self).create(vals)
        # 创建人不是申请人添加到关注者
        if self._context['uid'] != result.applicant.user_id.id:
            result.message_subscribe_users(user_ids=[result.applicant.user_id.id])

        return result

    @api.multi
    def write(self, vals):
        if vals.has_key('contract_id'):
            self.message_post(body=u"合同编号：%s --> %s" % (self.contract_id,vals['contract_id']))
        return super(dtdream_contract, self).write(vals)

    _sql_constraints = [
          ('contract_id_unique','unique(contract_id)','合同编号重复，请刷新页面重新填写！')
     ]
    @api.multi
    def wkf_draft(self):
        # 草稿状态

        self.current_handler_ids=""
        self.state='0'
        # self.write({'state':'0'})

    @api.multi
    def wkf_manager_review(self):
        # 主管审批
        if not self.attachment_ids:
            raise ValidationError('请先上传附件！')
        self.message_post(body=u"合同编号：%s，提交，提交时间：%s"%(self.contract_id,(datetime.now()+relativedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")))
        self.current_handler_ids=self.deparment_manage
        self.state='1'
        self.send_email()

    @api.multi
    def wkf_wait_review(self):
        # 待组织评审
        self.current_handler_ids=self.legal_interface
        self.state='2'
        self.send_email()

    @api.multi
    def wkf_review(self):
        # 评审中
        self.current_handler_ids=self.review_ids
        self.state='3'
        self.send_email()

    @api.multi
    def wkf_wait_countersign(self):
        # 待组织会签
        self.current_handler_ids=self.legal_interface
        self.state='4'
        self.send_email()

    @api.multi
    def wkf_countersign(self):
        # 会签中
        self.current_handler_ids=self.huiqian_ids
        self.state='5'
        self.send_email()

    @api.multi
    def wkf_sign(self):
        # 权签中
        self.current_handler_ids=self.quanqian_id
        self.state='6'
        self.send_email()

    @api.multi
    def wkf_stamp(self):
        # 待盖章
        self.current_handler_ids=self.stamp_id
        self.state='7'
        self.send_email()

    @api.multi
    def wkf_file(self):
        # 待归档
        self._compute_stamp()
        self.current_handler_ids=self.file_id
        self.state='8'
        self.send_email()

    @api.multi
    def wkf_done(self):
        self._compute_file()
        self.current_handler_ids=''
        self.state='9'

    @api.multi
    def wkf_void(self):
        self.current_handler_ids=''
        self.state='10'

    @api.multi
    def _message_track(self, tracked_fields, initial):
        self.ensure_one()
        changes = set()
        tracking_value_ids = []

        # generate tracked_values data structure: {'col_name': {col_info, new_value, old_value}}
        for col_name, col_info in tracked_fields.items():
            initial_value = initial[col_name]
            new_value = getattr(self, col_name)

            if new_value != initial_value and (new_value or initial_value):  # because browse null != False
                tracking = self.env['mail.tracking.value'].create_tracking_values(initial_value, new_value, col_name, col_info)
                if tracking:
                    tracking_value_ids.append([0, 0, tracking])

                if col_name in tracked_fields:
                    changes.add(col_name)
        return changes, tracking_value_ids

    @api.multi
    def message_track(self, tracked_fields, initial_values):

        return

    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, context=None, **kwargs):

        current_contract = self.pool.get('dtdream.contract').browse(cr, uid,thread_id,context=context)
        if kwargs.has_key('attachment_ids'):
            for id in kwargs['attachment_ids']:

                current_contract.att_final=self.pool.get('ir.attachment').browse(cr, uid,id,context=context).datas
                current_contract.att_final_name=self.pool.get('ir.attachment').browse(cr, uid,id,context=context).name
                base1 = current_contract.pool.get('ir.config_parameter').get_param(current_contract.env.cr,current_contract.env.user.id,'web.base.url')
                link1 = link='/web?#id=%s&view_type=form&model=dtdream.contract'%thread_id
                url1=base1+link1
                for people in current_contract.current_handler_ids:

                    mess = current_contract.env['mail.mail'].create({
                            'subject': u'%s于%s提交合同：%s 评审申请已经重新上传了附件，请您审批！' % (current_contract.applicant.name, current_contract.create_time[:10],current_contract.name),
                            'body_html': u'''
                            <p>%s，您好：</p>
                            <p>%s提交的合同评审已经重新上传了附件正等待您的审批！</p>
                            <p> 请点击链接进入审批:
                            <a href="%s">%s</a></p>
                            <p>dodo</p>
                            <p>万千业务，简单有do</p>
                            <p>%s</p>''' % (people.name, current_contract.applicant.name, url1, url1, current_contract.write_date[:10]),
                            'email_from':current_contract.env['ir.mail_server'].search([], limit=1).smtp_user,
                            'email_to': people.work_email,
                            # 'model': "",
                        })
                    mess.write({'model':""})
                    mess.send()



        return super(dtdream_contract, self).message_post(cr, uid, thread_id, context=context, **kwargs)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_contract, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"我的申请":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
            if res['type'] == "kanban":
                doc.xpath("//kanban")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res


class dtdream_contract_wizard(models.TransientModel):
     _name = "dtdream.contract.wizard"
     reason=fields.Text("意见")
     temp=fields.Char(string="存储信息")

     @api.one
     def btn_confirm(self):
          current_record=self.env['dtdream.contract'].browse(self._context['active_id'])
          # 添加历史审批人
          for people in current_record.current_handler_ids:
              current_record.write({"his_approve":[(4,self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).id)]})
          state=dict(self.env['dtdream.contract']._columns['state'].selection)[current_record.state]
          state_code=unicode(state,'utf-8')
          result = ''
          if not self.reason:
              self.reason=unicode('无','utf-8')
          if self.temp == 'agree':
              result = u'同意'
              current_record.write({'current_handler_ids':[(3,self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).id)]})
              if current_record.state == '2' or current_record.state == '4':
                  current_record.signal_workflow('btn_agree')
              else:
                  if len(current_record.current_handler_ids) == 0:
                      current_record.signal_workflow('btn_agree')
          # elif self.temp == 'refuse':
          #     current_record.message_post(body=u"审批意见%s" % self.reason)
          elif self.temp == 'norefer':
              result = u'不涉及'
              current_record.write({'current_handler_ids':[(3,self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).id)]})
              if len(current_record.current_handler_ids) == 0:
                  current_record.signal_workflow('btn_agree')
          elif self.temp == 'reject':
              result = u'驳回'
              current_record.signal_workflow('btn_reject')
          elif self.temp == 'force':
              result = u'强制通过'
              current_record.signal_workflow('btn_force_approve')
          elif self.temp == 'void':
              result = u'作废'
              current_record.signal_workflow('btn_void')
          elif self.temp == 'stamp':
              result = u'确认盖章'
              current_record.signal_workflow('btn_confirm_stamped')
          elif self.temp == 'file':
              result = u'确认归档'
              current_record.signal_workflow('btn_confirm_filed')
          current_record.message_post(body=u"审批意见：%s，%s" % (result,self.reason))


class dtdream_contract_type(models.Model):
    _name = "dtdream.contract.type"
    name = fields.Char(string="合同类型")
    name_id = fields.Char(string="编号")
    how_setting_approver = fields.Selection([('type', '按照合同类型'), ('subtype', '按照合同子类型')], string='审批人设置')

    @api.constrains('how_setting_approver')
    def check_approvers_set(self):
        if self.how_setting_approver == 'type':
            if not self.legal_interface or not self.review_ids or not self.huiqian_ids or not self.quanqian_id \
                    or not self.stamp_id or not self.file_id:
                raise ValidationError('请设置完所有审批人！')
    legal_interface = fields.Many2many('hr.employee', string="法务部接口人")
    review_ids = fields.Many2many('hr.employee', 'dtdream_contract_type_review', string="评审人")
    huiqian_ids = fields.Many2many('hr.employee', 'dtdream_contract_type_huiqian', string="会签人")
    quanqian_id = fields.Many2one('hr.employee', string="权签人")
    stamp_id = fields.Many2one('hr.employee', string="盖章处理人")
    file_id = fields.Many2one('hr.employee', string="归档处理人")


class dtdream_contract_subtype(models.Model):
    _name = "dtdream.contract.subtype"
    _description = u"合同子类型"
    name = fields.Char(string="合同子类型")
    parent_id = fields.Many2one('dtdream.contract.type',string="合同类型")
    name_id = fields.Char(string="编号")
    if_display_approver = fields.Boolean(string='是否显示审批人')

    @api.onchange('parent_id')
    def compute_if_display_approver(self):
        self.if_display_approver = False
        if self.parent_id.how_setting_approver == 'subtype':
            self.if_display_approver = True
    legal_interface = fields.Many2many('hr.employee', string="法务部接口人")
    review_ids = fields.Many2many('hr.employee', 'dtdream_contract_subtype_review', string="评审人")
    huiqian_ids = fields.Many2many('hr.employee', 'dtdream_contract_subtype_huiqian', string="会签人")
    quanqian_id = fields.Many2one('hr.employee', string="权签人")
    stamp_id = fields.Many2one('hr.employee', string="盖章处理人")
    file_id = fields.Many2one('hr.employee', string="归档处理人")

    @api.constrains('parent_id')
    def if_set_approvers(self):
        if self.parent_id.how_setting_approver == 'subtype':
            if not self.legal_interface or not self.review_ids or not self.huiqian_ids or not self.quanqian_id \
                    or not self.stamp_id or not self.file_id:
                raise ValidationError('请设置完所有审批人！')


class dtdream_contract_attachment(models.Model):
    _name = "dtdream.contract.attachment"
    _description = u"合同评审附件"
    contract_id = fields.Many2one("dtdream.contract", string="合同")
    attachment = fields.Binary(string="附件", store=True, required=1)
    attachment_name = fields.Char(string="附件名", invisible=1)
    attachment_remark = fields.Char(string="说明")
    attachment_upper = fields.Many2one('hr.employee', string='上传者', default = lambda self:self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]))





