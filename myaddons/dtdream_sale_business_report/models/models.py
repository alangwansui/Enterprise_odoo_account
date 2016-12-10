# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from lxml import etree
from openerp .exceptions import ValidationError
from openerp.osv import orm
import logging
import psycopg2
import openerp.tools as tools
import os
from openerp.tools.mimetypes import guess_mimetype

import itertools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

_logger = logging.getLogger(__name__)


class dtdream_deliver_object(models.Model):
    _name = "deliver.object"

    name = fields.Char(stirng="服务交付主体")

# 产品清单产品行类
class dtdream_product_line(models.Model):
    _inherit = 'dtdream.product.line'

    def _compute_is_pro_shenpiren(self):
        for rec in self:
            rec.is_pro_shenpiren = rec.product_business_line_id.is_pro_shenpiren
            rec.is_pro_shenpiren_value = rec.product_business_line_id.is_pro_shenpiren
            rec.is_bus_shenpiren = rec.product_business_line_id.is_bus_shenpiren
            rec.is_bus_shenpiren_value = rec.product_business_line_id.is_bus_shenpiren

    @api.one
    def _compute_is_pro_approveds(self):
        for pro_shenpiren in self.product_business_line_id.product_approveds:
            if self.env.user == pro_shenpiren.user_id:
                self.is_pro_approveds = True
                break
            else :
                self.is_pro_approveds = False
        for pro_shenpiren in self.product_business_line_id.business_approveds:
            if self.env.user == pro_shenpiren.user_id:
                self.is_business_approveds = True
                break
            else :
                self.is_business_approveds = False
        if self.product_business_line_id.state not in ('1','2','3') and self.report_is_current==True:
            self.is_business_approveds = True
        self.write({'report_state':self.product_business_line_id.state})
        self.write({'report_is_current':self.product_business_line_id.is_current})

    is_business_approveds = fields.Boolean(string="是否历史商务审批人",default=False,compute=_compute_is_pro_approveds)
    product_business_line_id = fields.Many2one('dtdream.sale.business.report',string="产品", ondelete='cascade', index=True, copy=False)
    product_line_id = fields.Many2one(required=False)
    report_state = fields.Char(string="报备流程状态",default="0")
    report_is_current = fields.Boolean(string="是否报备流程当前审批人",default=True)
    is_pro_approveds = fields.Boolean(string="是否历史产品审批人",default=False,compute=_compute_is_pro_approveds)
    is_pro_shenpiren = fields.Boolean(string="是否产品审批人",compute=_compute_is_pro_shenpiren)
    is_bus_shenpiren = fields.Boolean(string="是否商务审批人",compute=_compute_is_pro_shenpiren)
    send_type = fields.Selection([
        ('1','借货核销'),
        ('2','正常发货'),
        ('3','服务订单'),
    ],string='发货模式')

# 商务提前报备类
class dtdream_sale_business_report(models.Model):
    _name = 'dtdream.sale.business.report'
    _description = u"商务提前报备"
    _inherit = ['mail.thread']

    # _sql_constraints = [
    #     ('name_unique', 'UNIQUE(project_number)', "项目不能重复。"),
    # ]

    @api.one
    def _compute_is_current(self):
        self.is_current = False
        if self.apply_person == self.env['hr.employee'].search([('login','=',self.env.user.login)]) and self.state == "0":
            self.is_current = True
        for shenpiren in self.shenpiren:
            if self.env.user == shenpiren.user_id:
                self.is_current = True
        for pro_shenpiren in self.product_approveds:
            if self.env.user == pro_shenpiren.user_id:
                for rec in self.product_line:
                    rec.is_pro_approveds = True
                    self.write({'is_pro_approveds':True})
                break
            else :
                for rec in self.product_line:
                    rec.is_pro_approveds = False
                    self.write({'is_pro_approveds':False})
        for pro_shenpiren in self.business_approveds:
            if self.env.user == pro_shenpiren.user_id:
                for rec in self.product_line:
                    rec.is_business_approveds = True
                    self.write({'is_business_approveds':True})
                break
            else :
                for rec in self.product_line:
                    rec.is_business_approveds = False
                    self.write({'is_business_approveds':False})
        if self.state not in ('1','2','3') and self.is_current == True:
            for rec in self.product_line:
                    rec.is_business_approveds = True
        self.write({'warn_text':""})
        if len(self.shenpiren)==1 and self.shenpiren.user_id == self.env.user:
            if self.state == "6":
                if self.a_apply_discount < self.zhuren_grant_discount :
                    self.write({'warn_text':u'此项目总销售额%s万元，主任授权价%s万元，整单平均折扣（%s%%），已经超出您的审批权限。'%(self.total_chuhuo_price,self.total_zhuren_price,self.a_apply_discount)})
                else :
                    self.write({'warn_text':u'此项目总销售额%s万元，主任授权价%s万元，整单平均折扣（%s%%），在您的授权审批权限内。'%(self.total_chuhuo_price,self.total_zhuren_price,self.a_apply_discount)})
            if self.state == "7":
                if self.a_apply_discount < self.sale_grant_discount :
                    self.write({'warn_text':u'此项目成本%s万元，总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%），已经超出您的审批权限。'%(self.total_chengben,self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
                else :
                    self.write({'warn_text':u'此项目成本%s万元，总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%），在您的授权审批权限内。'%(self.total_chengben,self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
            if self.state == "8":
                if self.a_apply_discount < self.market_grant_discount :
                    self.write({'warn_text':u'此项目成本%s万元，总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%）,已经超出您的审批权限。'%(self.total_chengben,self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
                else :
                    self.write({'warn_text':u'此项目成本%s万元，总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%）,在您的授权审批权限内。'%(self.total_chengben,self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
            if self.state == "9":
                self.write({'warn_text':u'此项目成本%s万元，总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%）。'%(self.total_chengben,self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
        for rec in self.product_line:
            rec.write({'report_state':self.state})
        for rec in self.product_line:
            rec.write({'report_is_current':self.is_current})

    @api.multi
    def btn_finish(self):
        if self.state == "8":
            if self.if_out_grant == "1":
                raise ValidationError('已经超出您的审批权限，无法直接完成。')
        self.signal_workflow('btn_finish')

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def dtdream_send_mail(self, subject, content, email_to,appellation):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.sale.business.report' % self.id
        url = base_url+link
        email_to = email_to
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <a href="%s">点击进入查看</a></p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    @api.depends('product_line')
    def _onchange_product_line(self):
        list_price = 0
        apply_price = 0
        for rec in self.product_line:
            list_price = list_price + rec.list_price * rec.pro_num
            apply_price = apply_price + rec.list_price * rec.pro_num * rec.apply_discount * 0.01
        self.total_list_price = list_price
        self.total_apply_price = apply_price

    @api.onchange("system_department_id")
    def onchange_system_department(self):
        if self.system_department_id:
            if self.industry_id.parent_id != self.system_department_id:
                self.industry_id = ""
            return {
                'domain': {
                    "industry_id":[('parent_id','=',self.system_department_id.id)]
                }
            }

    @api.onchange("industry_id")
    def onchange_industry_id(self):
        if self.industry_id:
            self.system_department_id = self.industry_id.parent_id

    def _compute_is_pro_shenpiren(self):
        for record in self:
            if record.env.user.has_group("dtdream_sale.group_dtdream_office_product_vice_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_headquarters_server_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_server_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_system_product_vice_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_headquarters_product_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_product_director") or record.env.user.has_group("dtdream_sale.group_dtdream_management_product_vice_manager"):
                record.is_pro_shenpiren = True
            else:
                record.is_pro_shenpiren = False
            if record.env.user.has_group("dtdream_sale.group_dtdream_sale_office_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_marketing_department_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_marketing_department_vice_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_marketing_department_business_interface_person") or record.env.user.has_group("dtdream_sale.group_dtdream_system_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_system_vice_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_market_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_management_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_management_vice_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_company_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_devolopement_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_sale_high_manager") or record.env.user.has_group("dtdream_sale.group_dtdream_weekly_report_manager") :
                record.is_bus_shenpiren = True
            else:
                record.is_bus_shenpiren = False
            if record.create_uid == record.env.user.id:
                record.is_bus_shenpiren = True

    @api.depends("is_newest_record")
    def _compute_record_state(self):
        for rec in self:
            if rec.is_newest_record:
                rec.record_state = "1"
            else:
                rec.record_state = "0"

    @api.onchange("service_detail_selection")
    def _onchange_service_selection(self):
        if self.service_detail_selection != "other":
            self.service_detail = int(self.service_detail_selection)
        else:
            self.service_detail = ""

    import_button = fields.Char(string="导入产品清单",default="导入产品清单")
    download_button = fields.Char(string="下载导入模板",default="下载导入模板")
    has_import_button = fields.Boolean(string="是否可导入产品配置",default=False)
    is_approve_repeat = fields.Char(default=0,string="管理部部长与市场部部长是否重复")
    is_newest_record = fields.Boolean(string="是否最新记录",default=True)
    record_state = fields.Selection([
        ('0','无效'),
        ('1','有效')
    ],string="记录状态",compute=_compute_record_state,store=True)
    is_pro_shenpiren = fields.Boolean(string="是否产品审批人",default=False,compute=_compute_is_pro_shenpiren)
    is_bus_shenpiren = fields.Boolean(string="是否商务审批人",default=False,compute=_compute_is_pro_shenpiren)
    is_business_approveds = fields.Boolean(string="是否历史商务审批人",default=False)
    is_pro_approveds = fields.Boolean(string="是否历史产品审批人",default=False)
    pro_zongbu_finish = fields.Char(string='产品总部并行审批完成标识',default="0")
    pro_office_finish = fields.Char(string='办事处并行审批完成标识',default="0")
    name = fields.Char(default="商务提前报备")
    project_number = fields.Char(string="项目编号")
    rep_pro_name = fields.Many2one('crm.lead', string="项目名称", required=True,track_visibility='onchange')
    apply_person = fields.Many2one("hr.employee",string="申请人", default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).id, readonly=1)
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",required=True,track_visibility='onchange')
    industry_id = fields.Many2one("dtdream.industry", string="行业",required=True,track_visibility='onchange')
    office_id = fields.Many2one("dtdream.office", string="办事处",required=True,track_visibility='onchange')
    product_category_type_id = fields.Many2many("product.category", string="产品分类")
    total_list_price = fields.Float('目录价总计',store=True,compute=_onchange_product_line)
    total_apply_price = fields.Float('申请折扣价总计',store=True,compute=_onchange_product_line)
    need_ali_grant = fields.Selection([
        ('shi','是'),
        ('fou','否')
    ],string="是否需要阿里项目授权", required=True,track_visibility='onchange')
    bidding_time = fields.Date("招标时间",required=True,track_visibility='onchange')
    pre_implementation_time = fields.Date("预计开始实施时间", required=True,track_visibility='onchange')
    partner_id = fields.Many2one('res.partner',string="客户",required=True,track_visibility='onchange')
    final_partner_id = fields.Many2one('res.partner',string="最终用户",required=True,track_visibility='onchange')
    partner_budget = fields.Float(string="客户整体预算（万元）", required=True,track_visibility='onchange')
    have_hardware = fields.Selection([
        ('yse','是'),
        ('no','否')
    ],string="是否含硬件", required=True,track_visibility='onchange')
    supply_time = fields.Date(string="预计要货时间",required=True,track_visibility='onchange')
    apply_time = fields.Date(string="申请日期",default=lambda self:datetime.now(), required=True,track_visibility='onchange')
    pro_background = fields.Text(string="项目背景",track_visibility='onchange', required=True)
    apply_discription = fields.Text(string="商务申请说明",track_visibility='onchange', required=True)
    service_detail_selection = fields.Selection(
        [('1', '1'),
         ('2', '2'),
         ('3', '3'),
         ('4', '4'),
         ('5', '5'),
         ('other', '其他')],string="服务年限选择", required=True)
    service_detail = fields.Char(string="原厂维保或服务年限",track_visibility='onchange', required=True)
    channel_discription = fields.Text(string="渠道利润说明（产品和服务分开）",track_visibility='onchange', required=True)
    estimate_payment_condition = fields.Text(string="预计付款条件",track_visibility='onchange', required=True)
    # service_deliver_object = fields.Text(string="服务交付主体",track_visibility='onchange', required=True)
    service_deliver_object = fields.Many2many("deliver.object",string="服务交付主体", required=True)
    other_discription = fields.Text(string="其他特殊说明",track_visibility='onchange')
    project_promise = fields.Text(string="项目认定及承诺",readonly=True,default="对本项目的其他情况说明：本人确认此项目情况如前面所述，项目情况真实，代理商情况真实，价格情况真实。本人承诺如果今后此项目的方案产品配置数量、代理商、各级价格情况发生变化，本人将立刻向销售管理部商务更改申请，用新的审批表替换此表，对项目情况予以刷新。")
    if_promise = fields.Boolean(string="确认项目承诺",track_visibility='onchange')
    product_line = fields.One2many('dtdream.product.line', 'product_business_line_id', string='产品配置',copy=True)
    shenpiren = fields.Many2many('hr.employee', 's_t_e',string="当前审批人")
    shenpiren_version = fields.Char(string='审批版本',default="V1")
    approveds = fields.Many2many("hr.employee",'a_t_e', string="历史审批人")
    product_approveds = fields.Many2many("hr.employee",'p_a_t_e',string="历史产品审批人")
    business_approveds = fields.Many2many("hr.employee",'b_a_t_e',string="历史商务审批人")
    is_current = fields.Boolean(string="是否当前审批人", compute=_compute_is_current,default=True)
    a_apply_discount = fields.Float(string="平均折扣")
    sale_grant_discount = fields.Float(string="区域授权折扣")
    market_grant_discount = fields.Float(string="市场部授权折扣")
    total_chuhuo_price = fields.Float(string="总销售额(万元)")
    total_market_price = fields.Float(string="市场部授权价(万元)")
    total_sale_price = fields.Float(string="区域授权价(万元)")
    total_zhuren_price = fields.Float(string="办事处/系统部授权价(万元)")
    zhuren_grant_discount = fields.Float(string="主任授权折扣")
    total_chengben = fields.Float(string="项目成本(万元)")
    gross_profit = fields.Float(string="毛利(%)")
    if_out_grant = fields.Char(default=0)
    approve_records = fields.One2many("report.handle.approve.record","report_handle_id",string="审批记录")
    rejust_state = fields.Integer(string='驳回到销售',default=0)
    warn_text = fields.Char(compute=_compute_is_current,store=True)
    state = fields.Selection(
        [('0', '草稿'),
         ('2', '规范性审核、配置清单审核'),
         ('6', '办事处商务审批'),
         ('7', '区域商务审批'),
         ('8', '市场部商务审批'),
         ('9', '公司商务审批'),
         ('-1', '驳回'),
         ('done', '完成')], string="状态", default="0",track_visibility='onchange')
    file = fields.Binary(string="文件")
    file_name = fields.Char(string="文件名")
    remark = fields.Text(string="备注")
    if_gongkan = fields.Selection([
        ('1','已工勘'),
        ('0','未工勘'),
    ],string="是否已工勘")
    gongkan_content = fields.Text(string="工勘内容")
    not_gongkan_content  = fields.Text(string="工勘内容",default="未工勘")

    @api.multi
    def act_report_approve_crm(self):
        if_view_gongkan = False
        if self.state == '2':
            if self.office_id.name == u"总部":
                service_shenpiren = self.env['dtdream.business.shenpi.system.line'].search([('system_department_id','=',self.system_department_id.id)])[0].service_shenpiren
            else:
                service_shenpiren = self.env['dtdream.business.shenpi.line'].search([('office_id','=',self.office_id.id)])[0].service_shenpiren
            if service_shenpiren.id == self.env['hr.employee'].search([('login','=',self.env.user.login)]).id:
                if_view_gongkan = True
        view_id = self.env.ref('dtdream_sale_business_report.view_dtdream_report_approve_wizard_form').id
        action = {
                'name': '同意',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'dtdream.report.approve.wizard',
                'target':'new',
                'context': {'default_if_view_gongkan':if_view_gongkan,'default_gongkan_content':self.gongkan_content,'default_if_gongkan':self.if_gongkan},
                }
        return action

    @api.multi
    def wkf_draft(self):
        self.pro_zongbu_finish = "0"
        self.pro_office_finish = "0"
        self.write({'rejust_state':0,'state': '0',"shenpiren": [(6,0,[])]})
        self.rep_pro_name.sudo().write({'has_draft_business_report':True})

    def get_shenpiren(self):
        shenpiren = ""
        if self.state=="6":
            self.write({"shenpiren": [(6,0,[])]})
            if len(self.env['dtdream.shenpi.line'].search([('office_id','=',self.office_id.id)])) > 0 and self.office_id.code != 'H1':
                shenpiren = self.env['dtdream.shenpi.line'].search([('office_id','=',self.office_id.id)])[0].office_director
                if not shenpiren:
                    raise ValidationError('请先配置办事处主任')
                self.write({"shenpiren": [(4,[shenpiren.id])]})
            elif self.office_id.code != 'H1':
                raise ValidationError("请先配置办事处主任")
            if len(self.env['dtdream.shenpi.line.system'].search([('system_department_id','=',self.system_department_id.id)])) > 0:
                shenpiren = self.env['dtdream.shenpi.line.system'].search([('system_department_id','=',self.system_department_id.id)])[0].system_director
                if not shenpiren:
                    raise ValidationError('请先配置系统部部长')
                self.write({"shenpiren": [(4,[shenpiren.id])]})
            else :
                raise ValidationError("请先配置系统部部长")
            for shenpiren in self.shenpiren:
                self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您进行审核!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审核" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=shenpiren.work_email,
                       appellation = u'{0},您好：'.format(shenpiren.name))
        if self.state=="2":
            self.write({"shenpiren": [(6,0,[])]})
            # for pro_rec in self.product_line:
            #     categ_id = self.env['product.template'].search([('bom','=',pro_rec.bom)])[0].categ_id
            #     if len(self.env['dtdream.shenpi.by.product.line'].search([('categ_id','=',categ_id.id)])) > 0:
            #         pro_shenpiren = self.env['dtdream.shenpi.by.product.line'].search([('categ_id','=',categ_id.id)])[0].zongbu_product_charge
            #         if not pro_shenpiren:
            #             raise ValidationError('请先配置总部产品经理')
            #     else :
            #         raise ValidationError("请先配置总部产品经理")
            #     self.write({"product_approveds": [(4,[pro_shenpiren.id])]})
            #     self.write({"shenpiren": [(4,[pro_shenpiren.id])]})
            if len(self.env['dtdream.business.shenpi.line'].search([('office_id','=',self.office_id.id)])) > 0 and self.office_id.code != 'H1':
                business_interface_person = self.env['dtdream.business.shenpi.line'].search([('office_id','=',self.office_id.id)])[0].business_interface_person
                product_shenpiren = self.env['dtdream.business.shenpi.line'].search([('office_id','=',self.office_id.id)])[0].product_shenpiren
                service_shenpiren = self.env['dtdream.business.shenpi.line'].search([('office_id','=',self.office_id.id)])[0].service_shenpiren
                if not business_interface_person or not product_shenpiren or not service_shenpiren:
                    raise ValidationError('请先完成办事处规范性审核、配置清单审核配置')
                else:
                    self.write({"shenpiren": [(4,[business_interface_person.id])]})
                    self.write({"shenpiren": [(4,[product_shenpiren.id])]})
                    self.write({"shenpiren": [(4,[service_shenpiren.id])]})
            elif self.office_id.code != 'H1':
                raise ValidationError('请先完成办事处规范性审核、配置清单审核配置')
            if len(self.env['dtdream.business.shenpi.system.line'].search([('system_department_id','=',self.system_department_id.id)])) > 0 and self.office_id.code == 'H1':
                business_interface_person = self.env['dtdream.business.shenpi.system.line'].search([('system_department_id','=',self.system_department_id.id)])[0].business_interface_person
                product_shenpiren = self.env['dtdream.business.shenpi.system.line'].search([('system_department_id','=',self.system_department_id.id)])[0].product_shenpiren
                service_shenpiren = self.env['dtdream.business.shenpi.system.line'].search([('system_department_id','=',self.system_department_id.id)])[0].service_shenpiren
                if not business_interface_person or not product_shenpiren or not service_shenpiren:
                    raise ValidationError('请先完成系统部规范性审核、配置清单审核配置')
                else:
                    self.write({"shenpiren": [(4,[business_interface_person.id])]})
                    self.write({"shenpiren": [(4,[product_shenpiren.id])]})
                    self.write({"shenpiren": [(4,[service_shenpiren.id])]})
            elif self.office_id.code == 'H1':
                raise ValidationError('请先完成系统部规范性审核、配置清单审核配置')
            service_shenpiren = self.env['dtdream.shenpi.config'].search([])[0].zongbu_service_charge
            if not service_shenpiren:
                raise ValidationError('请先配置总部服务经理')
            # self.write({"product_approveds": [(4,[service_shenpiren.id])]})
            self.write({"shenpiren": [(4,[service_shenpiren.id])]})
            for shenpiren in self.shenpiren:
                self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您进行审核!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审核" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=shenpiren.work_email,
                       appellation = u'{0},您好：'.format(shenpiren.name))
        if self.state=="7":
            if len(self.env['dtdream.office.business.shenpi.line'].search([('office_ids.id','=',self.office_id.id)])) > 1:
                raise ValidationError("区域商务审批人配置重复")
            elif len(self.env['dtdream.office.business.shenpi.line'].search([('office_ids.id','=',self.office_id.id)])) == 1:
                shenpiren = self.env['dtdream.office.business.shenpi.line'].search([('office_ids.id','=',self.office_id.id)])[0].office_business_director
                if not shenpiren:
                    raise ValidationError("请先配置区域商务审批人")
            else:
                raise ValidationError("请先配置区域商务审批人")
            market_manager = self.env['dtdream.shenpi.config'].search([])[0].market_manager
            if not market_manager:
                raise ValidationError("请先配置市场部部长")
            if shenpiren.id == market_manager.id:
                self.is_approve_repeat = "1"
        if self.state=="8":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].market_manager
            if not shenpiren:
                raise ValidationError("请先配置市场部部长")
        if self.state=="9":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].company_manager
            if not shenpiren:
                raise ValidationError("请先配置公司总裁")
        return shenpiren

    @api.multi
    def wkf_approve2(self):
        self.write({'business_approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        if len(self.product_line)==0:
            raise ValidationError("请先导入产品配置后提交")
        for product in self.product_line:
            if product.list_price == 0:
                raise ValidationError("产品目录价不能为0")
            if not product.pro_num:
                raise ValidationError("产品数量不能为0")
            if product.apply_discount <= 0 or product.apply_discount > 100:
                raise ValidationError("申请折扣应在0%到100%之间")
        self.rep_pro_name.sudo().write({'has_draft_business_report':False})
        self.write({'state':'2'})
        self.get_shenpiren()

    @api.multi
    def wkf_approve6(self):
        # 计算各种总价及折扣，以及是否超权限
        total_chuhuo_price = 0
        total_chengben_price = 0
        total_market_price = 0
        total_zhuren_price = 0
        total_sale_price = 0
        total_chengben = 0
        i=0
        for product in self.product_line:
            i = i + 1
            real_pro = self.env['product.template'].search([('bom','=',product.bom)])[0]
            total_chuhuo_price = total_chuhuo_price + real_pro.list_price*product.pro_num*product.apply_discount/100
            total_chengben_price = total_chengben_price + product.list_price*product.pro_num
            total_market_price = total_market_price + real_pro.list_price*real_pro.market_president_discount*product.pro_num/100
            total_zhuren_price = total_zhuren_price + real_pro.list_price*real_pro.office_manager_discount*product.pro_num/100
            total_sale_price = total_sale_price + real_pro.list_price*real_pro.sale_grant_discount*product.pro_num/100
            total_chengben = total_chengben + real_pro.cost_price*product.pro_num
        self.total_chengben = round(total_chengben/10000,2)
        self.a_apply_discount = round(total_chuhuo_price*100/total_chengben_price,2)
        self.total_chuhuo_price = round(total_chuhuo_price/10000,2)
        self.total_market_price = round(total_market_price/10000,2)
        self.total_zhuren_price = round(total_zhuren_price/10000,2)
        self.total_sale_price = round(total_sale_price/10000,2)
        self.sale_grant_discount = round(total_sale_price*100/total_chengben_price,2)
        self.market_grant_discount = round(total_market_price*100/total_chengben_price,2)
        self.zhuren_grant_discount = round(total_zhuren_price*100/total_chengben_price,2)
        self.gross_profit = round(((total_chuhuo_price - total_chengben)/total_chuhuo_price)*100,2)
        self.pro_zongbu_finish = "0"
        self.write({'state':'6'})
        self.get_shenpiren()


    @api.multi
    def wkf_approve7(self):
        # 判断区域是否超权限审批
        self.pro_office_finish = "0"
        if self.a_apply_discount < self.sale_grant_discount :
            self.if_out_grant = 1
        else :
            self.if_out_grant = 0
        self.write({'state':'7'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您进行审核!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审批" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=self.shenpiren.work_email,
                       appellation = u'{0},您好：'.format(self.shenpiren.name))

    @api.multi
    def wkf_approve8(self):
        # 判断市场部部长是否超权限审批
        if self.a_apply_discount < self.market_grant_discount :
            self.if_out_grant = 1
        else :
            self.if_out_grant = 0
        self.write({'state':'8'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您进行审核!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审批" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=self.shenpiren.work_email,
                       appellation = u'{0},您好：'.format(self.shenpiren.name))

    @api.multi
    def wkf_approve9(self):
        self.write({'state':'9'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您进行审核!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审批" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=self.shenpiren.work_email,
                       appellation = u'{0},您好：'.format(self.shenpiren.name))

    @api.multi
    def wkf_done(self):
        self.write({'state':'done'})
        self.write({"shenpiren": [(6,0,[])]})

    # 豆腐块跳转到商务报备或选择项目后拷贝项目信息及产品清单
    @api.onchange("rep_pro_name")
    def _onchange_rep_pro_name(self):
        if self.env.context.get('active_id'):
            self.rep_pro_name = self.env['crm.lead'].search([('id','=', self.env.context.get('active_id'))])[0].id
        rec = self.env['dtdream.sale.business.report'].search([('rep_pro_name.id', '=', self.rep_pro_name.id)],order='create_date desc',limit=1)
        if rec:
            self.rep_pro_name = rec.rep_pro_name
            self.partner_id = rec.partner_id
            self.project_number = rec.project_number
            self.final_partner_id = rec.final_partner_id
            self.office_id = rec.office_id
            self.need_ali_grant = rec.need_ali_grant
            self.system_department_id = rec.system_department_id
            self.industry_id = rec.industry_id
            self.bidding_time = rec.bidding_time
            self.partner_budget = rec.partner_budget
            self.pre_implementation_time = rec.pre_implementation_time
            self.supply_time = rec.supply_time
            self.have_hardware = rec.have_hardware
            self.apply_time = rec.apply_time
            self.pro_background = rec.pro_background
            self.other_discription = rec.other_discription
            self.apply_discription = rec.apply_discription
            self.estimate_payment_condition = rec.estimate_payment_condition
            self.service_detail = rec.service_detail
            self.service_detail_selection = rec.service_detail_selection
            self.service_deliver_object = rec.service_deliver_object
            self.channel_discription = rec.channel_discription
            self.if_promise = rec.if_promise
            self.remark = rec.remark
            list = []
            for pro_rec in rec.product_line:
                vals = {'product_id':pro_rec.product_id,'bom':pro_rec.bom,'pro_type':pro_rec.pro_type,'pro_description':pro_rec.pro_description,'pro_name':pro_rec.pro_name,'list_price':pro_rec.list_price,'ref_discount':pro_rec.ref_discount,'apply_discount':pro_rec.apply_discount,'pro_num':pro_rec.pro_num,'config_set':pro_rec.config_set}
                list.append(vals)
            self.product_line = list
        else:
            self.system_department_id = self.rep_pro_name.system_department_id
            self.industry_id = self.rep_pro_name.industry_id
            self.product_category_type_id = self.rep_pro_name.product_category_type_id
            self.office_id = self.rep_pro_name.office_id
            self.bidding_time = self.rep_pro_name.bidding_time
            self.pre_implementation_time = self.rep_pro_name.pre_implementation_time
            self.partner_id = self.rep_pro_name.partner_id
            self.supply_time = self.rep_pro_name.supply_time
            self.project_number = self.rep_pro_name.project_number
            list = []
            for rec in self.rep_pro_name.product_line:
                vals = {'product_id':rec.product_id,'bom':rec.bom,'pro_type':rec.pro_type,'pro_description':rec.pro_description,'pro_name':rec.pro_name,'list_price':rec.list_price,'ref_discount':rec.ref_discount,'apply_discount':rec.apply_discount,'pro_num':rec.pro_num,'config_set':rec.config_set}
                list.append(vals)
            self.product_line = list

    # 报备中项目内容改变时回写到项目
    @api.constrains('system_department_id','industry_id','office_id','bidding_time','pre_implementation_time','partner_id','supply_time')
    def update_crm_data(self):
        self.env['crm.lead'].search([('id','=',self.rep_pro_name.id)]).write({'system_department_id':self.system_department_id.id,'industry_id':self.industry_id.id,'office_id':self.office_id.id,'bidding_time':self.bidding_time,'pre_implementation_time':self.pre_implementation_time,'partner_id':self.partner_id.id,'supply_time':self.supply_time})

    # 判断是否隐藏自定义分组
    @api.model
    def if_hide(self):
        if self.env.user.has_group('dtdream_sale.group_dtdream_sale_high_manager'):
            return False
        return True

    # 新建时刷新豆腐块数字
    @api.model
    def create(self, vals):
        if vals.has_key('if_promise') == False or vals['if_promise'] == False :
            raise ValidationError('请先确认项目承诺。')
        vals['project_number'] = self.env['crm.lead'].search([('id','=',vals['rep_pro_name'])])[0].project_number
        vals['has_import_button'] = True
        result = super(dtdream_sale_business_report, self).create(vals)
        records = self.env['dtdream.sale.business.report'].search([('rep_pro_name.id', '=', result.rep_pro_name.id)],order='create_date desc',limit=2)
        if len(records) == 2:
            records[1].write({'is_newest_record':False})
        old_business_count = self.env['crm.lead'].search([('id','=',result.rep_pro_name.id)])[0].business_count
        self.env['crm.lead'].search([('id','=',result.rep_pro_name.id)]).sudo().write({'business_count':old_business_count+1,'has_draft_business_report':True})
        return result

    @api.multi
    def write(self, vals):
        if len(vals) == 1 and (vals.has_key('warn_text') or vals.has_key('state')):
            return super(dtdream_sale_business_report, self).write(vals)
        if vals.has_key('if_promise'):
            if vals['if_promise'] == False:
                raise ValidationError('请先确认项目承诺。')
        elif self.if_promise == False:
            raise ValidationError('请先确认项目承诺。')
        if vals.has_key('rep_pro_name'):
            vals['project_number'] = self.env['crm.lead'].search([('id','=',vals['rep_pro_name'])])[0].project_number
        result = super(dtdream_sale_business_report, self).write(vals)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            if (rec.state == "0" and rec.create_uid.id == rec._uid) or rec.env.user.login=="admin" or rec.env.user.has_group("dtdream_sale.group_dtdream_sale_high_manager"):
                old_business_count = rec.env['crm.lead'].search([('id','=',rec.rep_pro_name.id)])[0].business_count
                rec.env['crm.lead'].search([('id','=',rec.rep_pro_name.id)]).sudo().write({'business_count':old_business_count-1})
                if rec.is_newest_record:
                    rec.env['crm.lead'].search([('id','=',rec.rep_pro_name.id)]).sudo().write({'has_draft_business_report':False})
                super(dtdream_sale_business_report, rec).unlink()
            else :
                raise ValidationError("只有草稿状态的报备申请可由创建者删除。")

    # 有记录时从豆腐块跳转到报备隐藏新建按钮
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        cr = self.env["dtdream.sale.business.report"].search([("rep_pro_name.id", "=", self.env.context.get('active_id'))])
        res = super(dtdream_sale_business_report, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        if res['type'] == "form":
            if len(cr):
                doc = etree.XML(res['arch'])
                doc.xpath("//form")[0].set("create", "false")
                res['arch'] = etree.tostring(doc)
        # 隐藏商务报备除我的申请外三个菜单下的新建按钮
        active_id = self._context.get('active_id', None)
        if res['type'] == "form":
            doc = etree.XML(res['arch'])
            if len(cr) or not active_id:
                doc.xpath("//form")[0].set("create", "false")
            res['arch'] = etree.tostring(doc)
        if res['type'] == "tree":
            if not active_id:
                doc = etree.XML(res['arch'])
                doc.xpath("//tree")[0].set("create", "false")
                res['arch'] = etree.tostring(doc)
        if self._context.get('params',None):
            if self.env['ir.actions.actions'].search([('id','=',self._context.get('params',None).get('action',None))])[0].name == u"我的申请":
                if res['type'] == "tree":
                    doc = etree.XML(res['arch'])
                    if len(cr) or not active_id:
                        doc.xpath("//tree")[0].set("create", "true")
                    res['arch'] = etree.tostring(doc)
                if res['type'] == "form":
                    doc = etree.XML(res['arch'])
                    if len(cr) or not active_id:
                        doc.xpath("//form")[0].set("create", "true")
                    res['arch'] = etree.tostring(doc)
        return res

# 项目管理类
class dtdream_crm_lead(models.Model):
    _inherit = 'crm.lead'

    business_count = fields.Integer(string="商务报备单据数量",default=0,readonly=True)
    has_draft_business_report = fields.Boolean(default=False,string="是否有草稿状态的报备单")

    @api.multi
    def action_dtdream_sale_business(self):
        if self.business_count == 0:
            if self.sale_apply_id.user_id.id != self._uid:
                raise ValidationError("只有营销责任人可以创建对应商务报备申请。")
        if not self.env['crm.lead'].search([('id','=', self.id)]):
            raise ValidationError("项目已归档，无法创建商务报备申请")
        cr = self.env['dtdream.sale.business.report'].search([('rep_pro_name.id', '=', self.id)],order='create_date desc',limit=1)
        res_id = cr.id if cr else ''
        import json
        context = json.loads(json.dumps(self._context))
        context.update({'active_id': self.id})
        action = {
            'name': '商务提前报备',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dtdream.sale.business.report',
            'res_id': res_id,
            'context': context,
            }
        return action

# 办事处主任配置行
class dtdream_shenpi_line(models.Model):
    _name = "dtdream.shenpi.line"

    shenpi_line_id = fields.Many2one('dtdream.shenpi.config')
    office_id = fields.Many2one("dtdream.office", string="办事处")
    office_director = fields.Many2one('hr.employee',string="办事处主任")


# 系统部部长配置行
class dtdream_shenpi_line_system(models.Model):
    _name = "dtdream.shenpi.line.system"

    shenpi_line_system_id = fields.Many2one('dtdream.shenpi.config')
    system_department_id = fields.Many2one("dtdream.industry", string="系统部")
    system_director = fields.Many2one('hr.employee',string="系统部部长")

# 办事处商务审批配置行
class dtdream_office_business_shenpi_line(models.Model):
    _name = "dtdream.office.business.shenpi.line"

    dtdream_office_business_shenpi_line_id = fields.Many2one('dtdream.shenpi.config')
    office_ids = fields.Many2many("dtdream.office", string="办事处")
    office_business_director = fields.Many2one('hr.employee',string="区域商务审批人")

# 商务审批人配置行
class dtdream_business_shenpi_line(models.Model):
    _name = "dtdream.business.shenpi.line"

    business_shenpi_line_id = fields.Many2one('dtdream.shenpi.config')
    office_id = fields.Many2one("dtdream.office", string="办事处")
    business_interface_person = fields.Many2one('hr.employee',string="订单接口人")
    product_shenpiren = fields.Many2one('hr.employee',string="产品审批人")
    service_shenpiren = fields.Many2one('hr.employee',string="服务审批人")

# 商务审批人配置行
class dtdream_business_shenpi_system_line(models.Model):
    _name = "dtdream.business.shenpi.system.line"

    business_shenpi_system_line_id = fields.Many2one('dtdream.shenpi.config')
    system_department_id = fields.Many2one("dtdream.industry", string="系统部")
    business_interface_person = fields.Many2one('hr.employee',string="订单接口人")
    product_shenpiren = fields.Many2one('hr.employee',string="产品审批人")
    service_shenpiren = fields.Many2one('hr.employee',string="服务审批人")

# 按产品线配置审批
# class dtdream_shenpi_by_product_line(models.Model):
#     _name = "dtdream.shenpi.by.product.line"
#
#     shenpi_by_product_line_id = fields.Many2one('dtdream.shenpi.config')
#     zongbu_product_charge = fields.Many2one('hr.employee',string="总部产品经理")
#     categ_id = fields.Many2one('product.category',string="产品线")


# 销售审批配置类
class dtdream_shenpi_config(models.Model):
    _name = "dtdream.shenpi.config"

    name = fields.Char(default="商务报备/报单审批配置")
    shenpi_line = fields.One2many('dtdream.shenpi.line','shenpi_line_id', string='销售办事处主任配置')
    shenpi_line_system = fields.One2many('dtdream.shenpi.line.system','shenpi_line_system_id', string='销售系统部部长配置')
    business_shenpi_line = fields.One2many('dtdream.business.shenpi.line','business_shenpi_line_id', string='办事处规范性审核、配置清单审核配置')
    business_shenpi_system_line = fields.One2many('dtdream.business.shenpi.system.line','business_shenpi_system_line_id', string='系统部规范性审核、配置清单审核配置')
    office_business_shenpi_line = fields.One2many('dtdream.office.business.shenpi.line','dtdream_office_business_shenpi_line_id', string='办事处商务审批配置')
    market_manager = fields.Many2one('hr.employee',string="市场部部长")
    company_manager = fields.Many2one('hr.employee',string="公司总裁")
    zongbu_service_charge = fields.Many2one('hr.employee',string="总部服务经理")

# 审批记录
class report_handle_approve_record(models.Model):
    _name = "report.handle.approve.record"
    _order = "id desc"

    name = fields.Char("审批环节")
    result = fields.Char("结果")
    liyou = fields.Text("审批意见")
    shenpiren = fields.Char("审批人")
    shenpiren_version = fields.Char("审批版本")
    report_handle_id = fields.Many2one("dtdream.sale.business.report",string="商务报备申请")

# 继承导入类
class dtdream_ir_import(orm.TransientModel):
    _inherit = 'base_import.import'

    def do(self, cr, uid, id, fields, options, dryrun=False, context=None):
        cr.execute('SAVEPOINT import')
        messages=[]

        (record,) = self.browse(cr, uid, [id], context=context)
        try:
            data, import_fields = self._convert_import_data(
                record, fields, options, context=context)
        except ValueError, e:
            return [{
                'type': 'error',
                'message': unicode(e),
                'record': False,
            }]
        if record.res_model == "dtdream.product.line":
            rec_id = context['params']['id']
            for rec in data:
                import_line = dict(zip(import_fields,rec))
                import_line['product_business_line_id'] = rec_id
                if not import_line.has_key('bom'):
                    messages.append(dict(type='error',
                                     message=u"导入文件中无bom编码，请添加后导入",
                                     moreinfo=""))
                    return messages
                if import_line.has_key('apply_discount') and len(import_line['apply_discount'].replace(' ','')) > 0:
                    if float(import_line['apply_discount']) > 100 or float(import_line['apply_discount']) <= 0:
                        messages.append(dict(type='error',
                                         message=u"申请折扣应在0%到100%之间",
                                         moreinfo=""))
                        return messages
                if import_line.has_key('send_type'):
                    if import_line['send_type'] and import_line['send_type'] not in (u'借货核销',u'正常发货',u'服务订单'):
                        messages.append(dict(type='error',
                                    message=u"导入发货模式信息错误，只有'借货核销'、'正常发货'、'服务订单'三种",
                                    moreinfo=""))
                        return messages
                    elif import_line['send_type'] in (u'借货核销',u'正常发货',u'服务订单'):
                        list = {
                            u'借货核销':'1',
                            u'正常发货':'2',
                            u'服务订单':'3',
                        }
                        import_line['send_type'] = list[import_line['send_type']]
                if len(self.pool["product.template"].search(cr,uid,[('bom','=',import_line['bom'])]))==1:
                    product_rec_id = self.pool["product.template"].search(cr,uid,[('bom','=',import_line['bom'])])[0]
                    product_rec = self.pool.get('product.template').browse(cr,uid,[product_rec_id])
                    import_line['pro_name'] = product_rec.name
                    import_line['pro_type'] = product_rec.pro_type.name
                    import_line['pro_description'] = product_rec.pro_description
                    import_line['list_price'] = product_rec.list_price
                    import_line['ref_discount'] = product_rec.ref_discount
                    if len(self.pool[record.res_model].search(cr,uid,[('bom','=',import_line['bom']),('product_business_line_id','=',rec_id)],limit=1))==1 :
                        old_rec_id = self.pool[record.res_model].search(cr,uid,[('bom','=',import_line['bom']),('product_business_line_id','=',rec_id)],limit=1)[0]
                        self.pool[record.res_model].write(cr, uid, [old_rec_id], import_line, context=context)
                    else:
                        self.pool[record.res_model].create(cr,uid,import_line,context=None)
                else:
                    messages.append(dict(type='error',
                                     message=u"bom编码[%s]无对应产品,请修改后导入"%import_line['bom'],
                                     moreinfo=""))
                    return messages
            return messages
        else:
            _logger.info('importing %d rows...', len(data))
            import_result = self.pool[record.res_model].load(
                cr, uid, import_fields, data, context=context)
            _logger.info('done')
            try:
                if dryrun:
                    cr.execute('ROLLBACK TO SAVEPOINT import')
                else:
                    cr.execute('RELEASE SAVEPOINT import')
            except psycopg2.InternalError:
                pass

            return import_result['messages']
