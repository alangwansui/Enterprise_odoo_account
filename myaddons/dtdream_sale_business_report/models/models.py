# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from lxml import etree

# 商务提前报备类
class dtdream_sale_business_report(models.Model):
    _name = 'dtdream.sale.business.report'
    _description = u"商务提前报备"
    _inherit = ['mail.thread']

    @api.one
    def _compute_is_current(self):
        if self.shenpiren.user_id == self.env.user:
            self.is_current = True
        else:
            self.is_current = False

    name = fields.Char(default="商务提前报备")
    rep_pro_name = fields.Many2one('crm.lead', string="项目名称", required=True,track_visibility='onchange')
    apply_person = fields.Char(string="申请人", default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).name, readonly=1)
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",required=True,track_visibility='onchange')
    industry_id = fields.Many2one("dtdream.industry", string="行业",required=True,track_visibility='onchange')
    office_id = fields.Many2one("dtdream.office", string="办事处",required=True,track_visibility='onchange')
    sale_money = fields.Float(string="销售金额", required=True,track_visibility='onchange')
    need_ali_grant = fields.Selection([
        ('shi','是'),
        ('fou','否')
    ],string="是否需要阿里项目授权", required=True,track_visibility='onchange')
    bidding_time = fields.Date("招标时间",required=True,track_visibility='onchange')
    pre_implementation_time = fields.Date("预计开始实施时间", required=True,track_visibility='onchange')
    partner_id = fields.Many2one('res.partner',string="客户",required=True,track_visibility='onchange')
    final_partner_id = fields.Many2one('res.partner',string="最终用户",required=True,track_visibility='onchange')
    partner_budget = fields.Float(string="客户整体预算", required=True,track_visibility='onchange')
    have_hardware = fields.Selection([
        ('yse','是'),
        ('no','否')
    ],string="是否含硬件", required=True,track_visibility='onchange')
    supply_time = fields.Date(string="预计要货时间",required=True,track_visibility='onchange')
    apply_time = fields.Date(string="申请日期",default=lambda self:datetime.now(), required=True,track_visibility='onchange')

    pro_background = fields.Text(string="项目背景",track_visibility='onchange')
    apply_discription = fields.Text(string="商务申请说明",track_visibility='onchange')
    service_detail = fields.Text(string="原厂维保或服务年限",track_visibility='onchange')
    channel_discription = fields.Text(string="渠道利润说明（产品和服务分开）",track_visibility='onchange')
    estimate_payment_condition = fields.Text(string="预计付款条件",track_visibility='onchange')
    service_deliver_object = fields.Text(string="服务交付主体",track_visibility='onchange')
    other_discription = fields.Text(string="其他特殊说明",track_visibility='onchange')
    project_promise = fields.Text(string="项目认定及承诺",readonly=True,default="对本项目的其他情况说明：本人确认此项目情况如前面所述，项目情况真实，代理商情况真实，价格情况真实。本人承诺如果今后此项目的方案产品配置数量、代理商、各级价格情况发生变化，本人将立刻向销售管理部商务更改申请，用新的审批表替换此表，对项目情况予以刷新。")
    if_promise = fields.Boolean(string="确认项目承诺",track_visibility='onchange')
    product_line = fields.One2many('dtdream.product.line', 'product_business_line_id', string='产品配置',copy=True)
    shenpiren = fields.Many2one('hr.employee', string="当前审批人")
    is_current = fields.Boolean(string="是否当前审批人", compute=_compute_is_current)

    approve_records = fields.One2many("report.handle.approve.record","report_handle_id",string="审批记录")

    rejust_state = fields.Integer(string='驳回到销售',default=0)
    state = fields.Selection(
        [('0', '草稿'),
         ('1', '配置产品'),
         ('2', '办事处审核产品'),
         ('3', '总部审核产品'),
         ('4', '完善商务'),
         ('5', '规范性审核'),
         ('6', '办事处商务审批'),
         ('7', '营销管理部商务审批'),
         ('8', '市场部商务审批'),
         ('9', '公司商务审批'),
         ('-1', '驳回'),
         ('done', '完成')], string="状态", default="0")

    @api.multi
    def wkf_draft(self):
        self.write({'state': '0'})

    def get_shenpiren(self):
        department = self.env['hr.employee'].search([('user_id','=',self.create_uid.id)]).department_id
        shenpiren = ""
        if self.state=="1":
            shenpiren = self.env['dtdream.shenpi.line'].search([('department','=',department.id)])[0].product_manager
        if self.state=="2":
            shenpiren = self.env['dtdream.shenpi.line'].search([('department','=',department.id)])[0].product_charge
        if self.state=="6":
            shenpiren = self.env['dtdream.shenpi.line'].search([('department','=',department.id)])[0].director
        if self.state=="3":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].zongbu_product_charge
        if self.state=="4":
            shenpiren = self.env['hr.employee'].search([('user_id','=',self.create_uid.id)])
        if self.state=="5":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].business_interface_person
        if self.state=="7":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].sales_manager
        if self.state=="8":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].market_manager
        if self.state=="9":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].company_manager
        return shenpiren

    @api.multi
    def wkf_approve1(self):
        self.write({'rejust_state':0})
        self.write({'state':'1'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": shenpiren.id})

    @api.multi
    def wkf_approve2(self):
        self.write({'state':'2'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": shenpiren.id})

    @api.multi
    def wkf_approve3(self):
        self.write({'state':'3'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": shenpiren.id})

    @api.multi
    def wkf_approve4(self):
        print self.state
        if self.state != "3":
            self.write({'rejust_state':1})
        self.write({'state':'4'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": shenpiren.id})

    @api.multi
    def wkf_approve5(self):
        self.write({'rejust_state':0})
        self.write({'state':'5'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": shenpiren.id})

    @api.multi
    def wkf_approve6(self):
        self.write({'state':'6'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": shenpiren.id})

    @api.multi
    def wkf_approve7(self):
        self.write({'state':'7'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": shenpiren.id})

    @api.multi
    def wkf_approve8(self):
        self.write({'state':'8'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": shenpiren.id})

    @api.multi
    def wkf_approve9(self):
        self.write({'state':'9'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": shenpiren.id})

    @api.multi
    def wkf_done(self):
        self.write({'state':'done'})
        self.write({"shenpiren": ""})

    # 豆腐块跳转到商务报备或选择项目后拷贝项目信息及产品清单
    @api.onchange("rep_pro_name")
    def _onchange_rep_pro_name(self):
        if self.env.context.get('active_id'):
            self.rep_pro_name = self.env['crm.lead'].search([('id','=', self.env.context.get('active_id'))])[0].id
        self.system_department_id = self.rep_pro_name.system_department_id
        self.industry_id = self.rep_pro_name.industry_id
        self.office_id = self.rep_pro_name.office_id
        self.bidding_time = self.rep_pro_name.bidding_time
        self.pre_implementation_time = self.rep_pro_name.pre_implementation_time
        self.partner_id = self.rep_pro_name.partner_id
        self.supply_time = self.rep_pro_name.supply_time
        list = []
        for rec in self.rep_pro_name.product_line:
            vals = {'product_id':rec.product_id,'bom':rec.bom,'pro_type':rec.pro_type,'pro_description':rec.pro_description,'pro_name':rec.pro_name,'list_price':rec.list_price,'ref_discount':rec.ref_discount,'apply_discount':rec.apply_discount,'pro_num':rec.pro_num,'config_set':rec.config_set}
            list.append(vals)
        self.product_line = list

    # 报备中项目内容改变时回写到项目
    @api.constrains('system_department_id','industry_id','office_id','bidding_time','pre_implementation_time','partner_id','supply_time')
    def update_crm_data(self):
        self.env['crm.lead'].search([('id','=',self.rep_pro_name.id)]).write({'system_department_id':self.system_department_id.id})
        self.env['crm.lead'].search([('id','=',self.rep_pro_name.id)]).write({'industry_id':self.industry_id.id})
        self.env['crm.lead'].search([('id','=',self.rep_pro_name.id)]).write({'office_id':self.office_id.id})
        self.env['crm.lead'].search([('id','=',self.rep_pro_name.id)]).write({'bidding_time':self.bidding_time})
        self.env['crm.lead'].search([('id','=',self.rep_pro_name.id)]).write({'pre_implementation_time':self.pre_implementation_time})
        self.env['crm.lead'].search([('id','=',self.rep_pro_name.id)]).write({'partner_id':self.partner_id.id})
        self.env['crm.lead'].search([('id','=',self.rep_pro_name.id)]).write({'supply_time':self.supply_time})

    # 新建时刷新豆腐块数字
    @api.model
    def create(self, vals):
        result = super(dtdream_sale_business_report, self).create(vals)
        self.env['crm.lead'].search([('id','=',result.rep_pro_name.id)]).write({'business_count':1})
        return result

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
        return res

# 产品清单产品行类
class dtdream_product_line(models.Model):
    _inherit = 'dtdream.product.line'

    product_business_line_id = fields.Many2one('dtdream.sale.business.report',string="产品", ondelete='cascade', index=True, copy=False)
    product_line_id = fields.Many2one(required=False)

# 项目管理类
class dtdream_crm_lead(models.Model):
    _inherit = 'crm.lead'

    business_count = fields.Integer(string="商务报备单据数量",default=0,readonly=True)

# 审批配置行
class dtdream_shenpi_line(models.Model):
    _name = "dtdream.shenpi.line"

    shenpi_line_id = fields.Many2one('dtdream.shenpi.config')

    department = fields.Many2one('hr.department',string="部门")
    product_manager = fields.Many2one('hr.employee',string="产品经理")
    product_charge = fields.Many2one('hr.employee',string="产品主管")
    director = fields.Many2one('hr.employee',string="主任")

# 销售审批配置类
class dtdream_shenpi_config(models.Model):
    _name = "dtdream.shenpi.config"

    name = fields.Char(default="销售审批配置")
    shenpi_line = fields.One2many('dtdream.shenpi.line','shenpi_line_id', string='销售审批配置',copy=True)
    zongbu_product_charge = fields.Many2one('hr.employee',string="总部产品主管")
    business_interface_person = fields.Many2one('hr.employee',string="商务接口人")
    sales_manager = fields.Many2one('hr.employee',string="营销管理部部长")
    market_manager = fields.Many2one('hr.employee',string="市场部总裁")
    company_manager = fields.Many2one('hr.employee',string="公司总裁")

# 审批记录
class report_handle_approve_record(models.Model):
    _name = "report.handle.approve.record"
    _order = "id desc"

    name = fields.Char("审批环节")
    result = fields.Char("结果")
    liyou = fields.Text("审批意见")
    shenpiren = fields.Char("审批人")
    report_handle_id = fields.Many2one("dtdream.sale.business.report",string="商务报备申请")
