# -*- coding: utf-8 -*-
import openerp
from openerp import http
from openerp.exceptions import ValidationError
from openerp.http import request, serialize_exception as _serialize_exception, _logger
from openerp import models, fields, api
import base64

from openerp.osv import osv
from openerp.tools.translate import _
import logging
import json

from openerp.http import serialize_exception
from datetime import datetime,time

import time
from lxml import etree


try:
    import xlwt
except ImportError:
    xlwt = None


class dtdream_contract(models.Model):
    _name = 'dtdream.contract'
    _inherit =['mail.thread']
    _description = u'合同评审电子流'
    his_approve=fields.Many2many('hr.employee',string="历史审批人")
    name = fields.Char(string="合同名称")

    @api.onchange('constract_type')
    def _compute_constract_id(self):
        if self.constract_type:
            max_constract_id=''
            # print self.env.cr.execute("SELECT * FROM dtdream_contract")
            baseid='DTD-'+self.constract_type.name_id+time.strftime("%Y%m%d", time.localtime())
            sql_baseid = baseid + "%"
            self._cr.execute("select constract_id from dtdream_contract where constract_id like '"+sql_baseid+"' order by id desc limit 1")
            for rec in self._cr.fetchall():
                print "rec",rec
                max_constract_id = rec[0]

            if max_constract_id:
                print "max_constract_id",max_constract_id
                max_id = max_constract_id[15:]
                print max_id
                print int(max_id)
                if int(max_id)<9:
                    self.constract_id_copy = baseid+'0'+str(int(max_id)+1)
                    self.constract_id = baseid+'0'+str(int(max_id)+1)
                else:
                    self.constract_id_copy = baseid+str(int(max_id)+1)
                    self.constract_id = baseid+str(int(max_id)+1)
            else:
                self.constract_id_copy = baseid+'01'
                self.constract_id = baseid+'01'

    constract_id=fields.Char(string="合同编号",store=True)
    constract_id_copy=fields.Char(string="合同编号_copy")
    constract_type=fields.Many2one("dtdream.contract.config",string="合同类型")
    constract_type_char=fields.Char(string="合同类型_copy")
    @api.onchange("constract_type")
    def _compute_people(self):
        print "--------------------"
        self.constract_type_char=self.constract_type.name
        config=self.env['dtdream.contract.config'].search([('name','=',self.constract_type.name)])
        self.legal_interface=config.legal_interface
        self.review_ids=config.review_ids
        self.huiqian_ids=config.huiqian_ids
        self.quanqian_id=config.quanqian_id
        self.stamp_id=config.stamp_id
        self.file_id=config.file_id
    applicant=fields.Many2one('hr.employee',string='申请人',default=lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]) )
    @api.one
    @api.onchange("applicant")
    def _compute_employee(self):
        print "+++++++++++++++++++++++++++",self
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
    deparment_manage=fields.Many2one('hr.employee',string="部门主管",compute=_compute_employee)
    state=fields.Selection([("0", "草稿"), ("1", "主管审批"), ("2", "待组织评审"),("3","评审中"),("4","待组织会签"),("5","会签中"),("6","权签中"),("7","待盖章"),("8","待归档"),("9","闭环"),("10","作废")],string="合同状态")
    create_time=fields.Datetime(string='创建时间',default=lambda self:datetime.now(),readonly=1)
    money=fields.Float(string="合同金额(元)")
    @api.onchange('money')
    def _compute_money_final(self):
        self.money_final = self.money

    money_final=fields.Float(string="合同最终金额(元)",help='合同最终金额由合同归档人录入')
    background=fields.Text(string="合同背景介绍")
    attachment=fields.Binary(string="合同附件（初稿）",store=True)
    attachment_name=fields.Char(string="附件名")
    att_final=fields.Binary(string="合同附件（终稿）")
    att_final_name=fields.Char(string="合同终稿附件名")
    remark=fields.Char(string="备注")
    pro_name=fields.Many2one("crm.lead",string="项目名称")
    # tip=fields.Char(default=lambda self:self.env['dtdream.contract.url'].search([],limit=1).name)

    @api.onchange('pro_name')
    def _compute_parter(self):
        try:
            self.partner=self.env['crm.lead'].search([('name','=',self.pro_name.name)]).partner_id.name
        except:
            return


    partner=fields.Char(string="合作方",compute=_compute_parter)
    provider=fields.Many2one('res.partner',string='合作方',domain=[('supplier','=',True)])
    is_standard=fields.Boolean(string="是否标准合同",help='标准合同无需评审，直接进入会签环节，可快速完成合同评审流程')
    current_handler_ids=fields.Many2many('hr.employee','c_i_h_e',string="当前处理人",store=True)

    @api.one
    def _compute_is_handler(self):
        for handler in self.current_handler_ids:
            if handler.user_id.id == self.env.user.id:
                self.is_handler = True

    @api.one
    def _compute_is_legal_interface(self):
        self.is_legal_interface = False
        for people in self.legal_interface:
            if people.user_id.id == self.env.user.id:
                self.is_legal_interface = True
    is_handler=fields.Boolean("是否当前处理人",compute=_compute_is_handler)
    is_legal_interface=fields.Boolean("是否法务部接口人",compute=_compute_is_legal_interface)
    legal_interface=fields.Many2many('hr.employee','dt_contract_legal_interface',string="法务接口人")
    review_ids=fields.Many2many('hr.employee','r_i_h_e',string="评审人",store=True)
    huiqian_ids=fields.Many2many('hr.employee','h_i_h_e',string="会签人")
    quanqian_id=fields.Many2one('hr.employee',string="权签人")
    stamp_id=fields.Many2one('hr.employee',string="盖章处理人")

    def _compute_stamp(self):
        self.is_stamped=True
        self.stamp_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


    def _compute_file(self):
        self.is_filed=True
        self.file_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    is_stamped=fields.Boolean(string="是否盖章")
    stamp_time=fields.Char(string="盖章时间")
    file_id=fields.Many2one('hr.employee',string="归档处理人")
    is_filed=fields.Boolean(string="是否归档")
    is_file_id=fields.Boolean(string='是否归档人',compute=_compute_is_applicant)
    file_time=fields.Char(string="归档时间")
    review2wait_countersign=fields.Boolean(default=False)

    def send_email(self,cr,uid,id):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')

        link='/web?#id=%s&view_type=form&model=dtdream.contract'%id
        url=base_url+link
        damn_self=self.pool.get('dtdream.contract').browse(cr, uid,id)
        for people in damn_self.current_handler_ids:
            damn_self.env['mail.mail'].create({
                    'subject': u'%s于%s提交合同：%s 评审申请，请您审批！' % (damn_self.applicant.name, damn_self.create_time[:10],damn_self.name),
                    'body_html': u'''
                    <p>%s，您好：</p>
                    <p>%s提交的合同评审正等待您的审批！</p>
                    <p> 请点击链接进入审批:
                    <a href="%s">%s</a></p>
                    <p>dodo</p>
                    <p>万千业务，简单有do</p>
                    <p>%s</p>''' % (people.name, damn_self.applicant.name, url, url, damn_self.write_date[:10]),
                    'email_from':damn_self.env['ir.mail_server'].search([], limit=1).smtp_user,
                    'email_to': people.work_email,
                }).send()
        return url



    @api.model
    def create(self,vals):
        config=self.env['dtdream.contract.config'].search([('name','=',vals['constract_type_char'])])
        result=super(dtdream_contract,self).create(vals)
        # 对只读字段重新写入
        result.legal_interface=config.legal_interface
        result.huiqian_ids=config.huiqian_ids
        result.quanqian_id=config.quanqian_id
        result.stamp_id=config.stamp_id
        result.file_id=config.file_id
        result.money_final=result.money
        result.constract_id=result.constract_id_copy
        # result.message_post(body=u"--------------：%s"%time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        # 创建人不是申请人添加到关注者
        if self._context['uid'] != result.applicant.user_id.id:
            result.message_subscribe_users(user_ids=[result.applicant.user_id.id])

        return result
    @api.multi
    def write(self, vals):
        print "write--------"
        print self
        print self.state
        print vals
        if self.state == '0':

            if vals.has_key('money'):
                print "monet",self.money
                self.money_final=vals['money']
            if vals.has_key('constract_type_char'):
                config=self.env['dtdream.contract.config'].search([('name','=',vals['constract_type_char'])])
                self.legal_interface=config.legal_interface
                self.huiqian_ids=config.huiqian_ids
                self.quanqian_id=config.quanqian_id
                self.stamp_id=config.stamp_id
                self.file_id=config.file_id

                self.constract_id=vals['constract_id_copy']
        result = super(dtdream_contract, self).write(vals)
        # print oooo


        return result

    _sql_constraints = [
          ('constract_id_unique','unique(constract_id)','合同编号重复，请刷新页面重新填写！')
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
        self.message_post(body=u"合同编号：%s，提交，提交时间：%s"%(self.constract_id,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
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
        print "message_post"
        """ Redirect the posting of message on res.users to the related employee.
            This is done because when giving the context of Chatter on the
            various mailboxes, we do not have access to the current partner_id. """

        current_contract = self.pool.get('dtdream.contract').browse(cr, uid,thread_id,context=context)
        if kwargs.has_key('attachment_ids'):
            for id in kwargs['attachment_ids']:
                print "attachment_ids",id
                current_contract.att_final=self.pool.get('ir.attachment').browse(cr, uid,id,context=context).datas
                current_contract.att_final_name=self.pool.get('ir.attachment').browse(cr, uid,id,context=context).name
                base1 = current_contract.pool.get('ir.config_parameter').get_param(current_contract.env.cr,current_contract.env.user.id,'web.base.url')
                link1 = link='/web?#id=%s&view_type=form&model=dtdream.contract'%thread_id
                url1=base1+link1
                for people in current_contract.current_handler_ids:
                    print "dddddddddddddd"
                    print current_contract
                    print current_contract.name
                    current_contract.env['mail.mail'].create({
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
                        }).send()

        return super(dtdream_contract, self).message_post(cr, uid, thread_id, context=context, **kwargs)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_contract, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name == u"待我审批" or my_action.name == u"我已审批" or my_action.name == u"所有合同":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
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
          if not self.reason:
              self.reason=unicode('无','utf-8')
          if self.temp == 'agree':
              current_record.write({'current_handler_ids':[(3,self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).id)]})
              current_record.message_post(body=u"合同编号：%s, 状态：%s, 审批人：%s, 审批结果：同意, 审批意见：%s, 审批时间：%s" %(current_record.constract_id,state_code,self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,self.reason,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
              if current_record.state == '2' or current_record.state == '4':
                  current_record.signal_workflow('btn_agree')
              else:
                  if len(current_record.current_handler_ids) == 0:
                      current_record.signal_workflow('btn_agree')
          elif self.temp == 'refuse':
              current_record.message_post(body=u"合同编号：%s, 状态：%s, 审批人：%s, 审批结果：<span style='color:red'>不同意</span>, 审批意见：%s, 审批时间：%s" %(current_record.constract_id,state_code,self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,self.reason,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
          elif self.temp == 'norefer':
              current_record.write({'current_handler_ids':[(3,self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).id)]})
              current_record.message_post(body=u"合同编号：%s, 状态：%s, 审批人：%s, 审批结果：不涉及, 审批意见：%s, 审批时间：%s" %(current_record.constract_id,state_code,self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,self.reason,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
              if len(current_record.current_handler_ids) == 0:
                  current_record.signal_workflow('btn_agree')
          elif self.temp == 'reject':
              current_record.message_post(body=u"合同编号：%s, 状态：%s, 审批人：%s, 审批结果：<span style='color:red'>驳回</span>, 审批意见：%s, 审批时间：%s" %(current_record.constract_id,state_code,self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,self.reason,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
              current_record.signal_workflow('btn_reject')
          elif self.temp == 'force':
              current_record.message_post(body=u"合同编号：%s, 状态：%s, 审批人：%s, 审批结果：强制通过, 审批意见：%s, 审批时间：%s" %(current_record.constract_id,state_code,self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,self.reason,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
              current_record.signal_workflow('btn_force_approve')
          elif self.temp == 'void':
              current_record.message_post(body=u"合同编号：%s, 状态：%s, 审批人：%s, 审批结果：作废, 审批意见：%s, 审批时间：%s" %(current_record.constract_id,state_code,self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,self.reason,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
              current_record.signal_workflow('btn_void')
          elif self.temp == 'stamp':
              current_record.message_post(body=u"合同编号：%s, 状态：%s, 审批人：%s, 审批结果：确认盖章, 审批意见：%s, 审批时间：%s" %(current_record.constract_id,state_code,self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,self.reason,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
              current_record.signal_workflow('btn_confirm_stamped')
          elif self.temp == 'file':
              current_record.message_post(body=u"合同编号：%s, 状态：%s, 审批人：%s, 审批结果：确认归档, 审批意见：%s, 审批时间：%s" %(current_record.constract_id,state_code,self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,self.reason,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
              current_record.signal_workflow('btn_confirm_filed')

class dtdream_contract_config(models.Model):
    _name = "dtdream.contract.config"
    name=fields.Char(string="合同类型")
    name_id=fields.Char(string="合同类型ID")
    legal_interface=fields.Many2many('hr.employee',string="法务部接口人")
    review_ids=fields.Many2many('hr.employee','dtdream_contract_config_review',string="评审人")
    huiqian_ids=fields.Many2many('hr.employee','dtdream_contract_config_huiqian',string="会签人")
    quanqian_id=fields.Many2one('hr.employee',string="权签人")
    stamp_id=fields.Many2one('hr.employee',string="盖章处理人")
    file_id=fields.Many2one('hr.employee',string="归档处理人")

# class dtdream_contract_url(models.Model):
#     _name = "dtdream.contract.url"
#     name = fields.Char(string="标准合同下载地址")



