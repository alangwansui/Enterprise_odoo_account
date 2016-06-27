# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from lxml import etree
from openerp .exceptions import ValidationError

# 产品清单产品行类
class dtdream_product_line(models.Model):
    _inherit = 'dtdream.product.line'

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
    report_state = fields.Char(string="报备流程状态",default="1")
    report_is_current = fields.Boolean(string="是否报备流程当前审批人",default=True)
    # report_create = fields.Char(string="是否可创建产品")
    is_pro_approveds = fields.Boolean(string="是否历史产品审批人",default=False,compute=_compute_is_pro_approveds)
    remark = fields.Selection([
        ('1','借货核销'),
        ('2','正常发货'),
        ('3','服务订单'),
    ],string='备注')


# 商务提前报备类
class dtdream_sale_business_report(models.Model):
    _name = 'dtdream.sale.business.report'
    _description = u"商务提前报备"
    _inherit = ['mail.thread']

    _sql_constraints = [
        ('name_unique', 'UNIQUE(project_number)', "项目不能重复。"),
    ]

    @api.one
    def _compute_is_current(self):
        self.is_current = False
        if self.state == "0":
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
                    self.write({'warn_text':u'此项目总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%），已经超出您的审批权限。'%(self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
                else :
                    self.write({'warn_text':u'此项目总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%），在您的授权审批权限内。'%(self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
            if self.state == "8":
                if self.a_apply_discount < self.market_grant_discount :
                    self.write({'warn_text':u'此项目总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%）,已经超出您的审批权限。'%(self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
                else :
                    self.write({'warn_text':u'此项目总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%）,在您的授权审批权限内。'%(self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
            if self.state == "9":
                self.write({'warn_text':u'此项目总销售额%s万元，主任授权价%s万元，营销管理部授权价%s万元，市场部授权价%s万元，整单平均折扣（%s%%）。'%(self.total_chuhuo_price,self.total_zhuren_price,self.total_sale_price,self.total_market_price,self.a_apply_discount)})
        for rec in self.product_line:
            rec.write({'report_state':self.state})
        for rec in self.product_line:
            rec.write({'report_is_current':self.is_current})
        # if self.state == "1" and self.is_current == "True":
        #     self.product_line.write({'report_create':"1"})
        # else:
        #     self.product_line.write({'report_create':"0"})


    @api.onchange("sale_business_interface_person")
    def _onchange_sale_business_interface_person(self):
        if self.state == "0":
            self.is_current = True
        rec = self.env['dtdream.shenpi.config'].search([])
        if rec:
            business_interface_person = self.env['dtdream.shenpi.config'].search([])[0].business_interface_person
            persons = []
            if business_interface_person:
                for x in business_interface_person:
                    persons.append(x.id)
                return {'domain': {'sale_business_interface_person': [('id', 'in', persons)]}}
            else:
                return {'domain': {'sale_business_interface_person': [('id', '=', False)]}}

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

    is_business_approveds = fields.Boolean(string="是否历史商务审批人",default=False)
    is_pro_approveds = fields.Boolean(string="是否历史产品审批人",default=False)
    pro_zongbu_finish = fields.Char(string='产品总部并行审批完成标识',default="0")
    name = fields.Char(default="商务提前报备")
    project_number = fields.Char(string="项目编号")
    rep_pro_name = fields.Many2one('crm.lead', string="项目名称", required=True,track_visibility='onchange')
    apply_person = fields.Char(string="申请人", default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).name, readonly=1)
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",required=True,track_visibility='onchange')
    industry_id = fields.Many2one("dtdream.industry", string="行业",required=True,track_visibility='onchange')
    office_id = fields.Many2one("dtdream.office", string="办事处",required=True,track_visibility='onchange')
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
    shenpiren = fields.Many2many('hr.employee', 's_t_e',string="当前审批人")
    shenpiren_version = fields.Char(string='审批版本',default="V1")

    approveds = fields.Many2many("hr.employee",'a_t_e', string="历史审批人")
    product_approveds = fields.Many2many("hr.employee",'p_a_t_e',string="历史产品审批人")
    business_approveds = fields.Many2many("hr.employee",'b_a_t_e',string="历史商务审批人")
    is_current = fields.Boolean(string="是否当前审批人", compute=_compute_is_current)

    a_apply_discount = fields.Float(string="平均折扣")
    sale_grant_discount = fields.Float(string="营销管理部授权折扣")
    market_grant_discount = fields.Float(string="市场部授权折扣")
    # maoli = fields.Float(string="毛利")
    total_chuhuo_price = fields.Float(string="总销售额")
    total_market_price = fields.Float(string="市场部部长授权价")
    total_sale_price = fields.Float(string="营销管理部授权价")
    total_zhuren_price = fields.Float(string="主任授权价")
    zhuren_grant_discount = fields.Float(string="主任授权折扣")


    if_out_grant = fields.Char(default=0)
    product_manager = fields.Many2one('hr.employee',string="产品SE（配置产品人员）",required=True)
    sale_business_interface_person = fields.Many2one('hr.employee',string="商务接口人",required=True)

    approve_records = fields.One2many("report.handle.approve.record","report_handle_id",string="审批记录")

    rejust_state = fields.Integer(string='驳回到销售',default=0)
    warn_text = fields.Char()
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
         ('done', '完成')], string="状态", default="0",track_visibility='onchange')

    @api.multi
    def wkf_draft(self):
        self.write({'state': '0'})

    def get_shenpiren(self):
        department = self.env['hr.employee'].search([('user_id','=',self.create_uid.id)]).department_id
        shenpiren = ""
        if self.state=="1":
            shenpiren = self.product_manager
        if self.state=="2":
            if len(self.env['dtdream.shenpi.line'].search([('department','=',department.id)])) > 0:
                shenpiren = self.env['dtdream.shenpi.line'].search([('department','=',department.id)])[0].product_charge
            else :
                raise ValidationError('请先配置产品主管')
        if self.state=="6":
            shenpiren = self.env['dtdream.shenpi.line'].search([('department','=',department.id)])[0].director
            if not shenpiren:
                raise ValidationError("请先配置部门主管")
        if self.state=="3":
            self.write({"shenpiren": [(6,0,[])]})
            for pro_rec in self.product_line:
                categ_id = self.env['product.template'].search([('bom','=',pro_rec.bom)])[0].categ_id
                if len(self.env['dtdream.shenpi.by.product.line'].search([('categ_id','=',categ_id.id)])) > 0:
                    pro_shenpiren = self.env['dtdream.shenpi.by.product.line'].search([('categ_id','=',categ_id.id)])[0].zongbu_product_charge
                    if not pro_shenpiren:
                        raise ValidationError('请先配置总部产品经理')
                    service_shenpiren = self.env['dtdream.shenpi.by.product.line'].search([('categ_id','=',categ_id.id)])[0].zongbu_service_charge
                    if not service_shenpiren:
                        raise ValidationError('请先配置总部服务经理')
                else :
                    raise ValidationError("请先配置总部产品经理与服务经理")
                self.write({"shenpiren": [(4,[pro_shenpiren.id])]})
                self.write({"shenpiren": [(4,[service_shenpiren.id])]})
            for shenpiren in self.shenpiren:
                self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您审核产品配置!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审核产品配置" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=shenpiren.work_email,
                       appellation = u'{0},您好：'.format(shenpiren.name))
        if self.state=="4":
            shenpiren = self.env['hr.employee'].search([('user_id','=',self.create_uid.id)])
        if self.state=="5":
            shenpiren = self.sale_business_interface_person
        if self.state=="7":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].sales_manager
            if not shenpiren:
                raise ValidationError("请先配置营销管理部部长")
        if self.state=="8":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].market_manager
            if not shenpiren:
                raise ValidationError("请先配置市场部总裁")
        if self.state=="9":
            shenpiren = self.env['dtdream.shenpi.config'].search([])[0].company_manager
            if not shenpiren:
                raise ValidationError("请先配置公司总裁")
        return shenpiren

    @api.multi
    def wkf_approve1(self):
        self.write({'business_approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        self.pro_zongbu_finish = "0"
        self.write({'rejust_state':0})
        self.write({'state':'1'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您配置产品!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您配置产品" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=self.shenpiren.work_email,
                       appellation = u'{0},您好：'.format(self.shenpiren.name))

    @api.multi
    def wkf_approve2(self):
        if len(self.product_line)==0:
            raise ValidationError("至少添加一行产品才可提交审核")
        for product in self.product_line:
            if product.list_price == 0:
                raise ValidationError("产品目录价不能为0")
            if not product.pro_num:
                raise ValidationError("产品数量不能为0")

        self.write({'state':'2'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您审核产品配置!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审核产品配置" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=self.shenpiren.work_email,
                       appellation = u'{0},您好：'.format(self.shenpiren.name))

    @api.multi
    def wkf_approve3(self):
        self.write({'state':'3'})
        self.get_shenpiren()

    @api.multi
    def wkf_approve4(self):
        self.pro_zongbu_finish = "0"
        if self.state != "3":
            self.write({'rejust_state':1})
        self.write({'state':'4'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您完善商务信息!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您完善商务信息" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=self.shenpiren.work_email,
                       appellation = u'{0},您好：'.format(self.shenpiren.name))


    @api.multi
    def wkf_approve5(self):
        for product in self.product_line:
            if not product.apply_discount:
                raise ValidationError("产品申请折扣不能为0")
        self.write({'rejust_state':0})
        self.write({'state':'5'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您审批!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审批" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=self.shenpiren.work_email,
                       appellation = u'{0},您好：'.format(self.shenpiren.name))


    @api.multi
    def wkf_approve6(self):
        # 计算各种总价及折扣，以及是否超权限
        total_chuhuo_price = 0
        total_chengben_price = 0
        total_market_price = 0
        total_zhuren_price = 0
        i=0
        for product in self.product_line:
            i = i + 1
            real_pro = self.env['product.template'].search([('bom','=',product.bom)])[0]
            total_chuhuo_price = total_chuhuo_price + real_pro.list_price*product.pro_num*product.apply_discount/100
            total_chengben_price = total_chengben_price + product.list_price*product.pro_num
            total_market_price = total_market_price + real_pro.list_price*real_pro.market_president_discount*product.pro_num/100
            total_zhuren_price = total_zhuren_price + real_pro.list_price*real_pro.office_manager_discount*product.pro_num/100
        self.a_apply_discount = round(total_chuhuo_price*100/total_chengben_price,2)
        self.sale_grant_discount = round(self.env['dtdream.shenpi.config'].search([])[0].sale_grant_discount,2)
        self.total_chuhuo_price = round(total_chuhuo_price/10000,2)
        self.total_market_price = round(total_market_price/10000,2)
        self.total_zhuren_price = round(total_zhuren_price/10000,2)
        self.total_sale_price = round(total_chuhuo_price*(self.env['dtdream.shenpi.config'].search([])[0].sale_grant_discount/1000000),2)
        self.market_grant_discount = round(total_market_price*100/total_chengben_price,2)
        self.zhuren_grant_discount = round(total_zhuren_price*100/total_chengben_price,2)
        # self.maoli = round((total_chuhuo_price - total_chengben_price)/total_chuhuo_price)

        self.pro_zongbu_finish = "0"
        self.write({'state':'6'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您审批!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审批" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=self.shenpiren.work_email,
                       appellation = u'{0},您好：'.format(self.shenpiren.name))


    @api.multi
    def wkf_approve7(self):
        # 判断营销管理部是否超权限审批
        if self.a_apply_discount < self.sale_grant_discount :
            self.if_out_grant = 1
        else :
            self.if_out_grant = 0
        self.write({'state':'7'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您审批!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
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
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您审批!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                       u"%s提交了商务提前报备申请,等待您审批" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=self.shenpiren.work_email,
                       appellation = u'{0},您好：'.format(self.shenpiren.name))


    @api.multi
    def wkf_approve9(self):
        self.write({'state':'9'})
        shenpiren = self.get_shenpiren()
        self.write({"shenpiren": [(6,0,[shenpiren.id])]})
        self.dtdream_send_mail(u"{0}于{1}提交了商务提前报备申请,请您审批!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
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
        self.system_department_id = self.rep_pro_name.system_department_id
        self.industry_id = self.rep_pro_name.industry_id
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
        if vals.has_key('if_promise') == False or vals['if_promise'] == False :
            raise ValidationError('请先确认项目承诺。')
        vals['project_number'] = self.env['crm.lead'].search([('id','=',vals['rep_pro_name'])])[0].project_number
        result = super(dtdream_sale_business_report, self).create(vals)
        self.env['crm.lead'].search([('id','=',result.rep_pro_name.id)]).write({'business_count':1})
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
        if (self.state == "0" and self.create_uid.id == self._uid) or self.env.user.login=="admin":
            self.env['crm.lead'].search([('id','=',self.rep_pro_name.id)]).write({'business_count':0})
            return super(dtdream_sale_business_report, self).unlink()
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

    @api.multi
    def action_dtdream_sale_business(self):
        if self.business_count == 0:
            if self.sale_apply_id.user_id.id != self._uid:
                raise ValidationError("只有营销责任人可以创建对应商务报备申请。")
        cr = self.env['dtdream.sale.business.report'].search([('rep_pro_name.id', '=', self.id)])
        res_id = cr.id if cr else ''
        action = {
            'name': '商务提前报备',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dtdream.sale.business.report',
            'res_id': res_id,
            'context': self._context,
            }
        return action

# 审批配置行
class dtdream_shenpi_line(models.Model):
    _name = "dtdream.shenpi.line"

    shenpi_line_id = fields.Many2one('dtdream.shenpi.config')

    department = fields.Many2one('hr.department',string="部门")
    product_charge = fields.Many2one('hr.employee',string="产品主管")
    director = fields.Many2one('hr.employee',string="部门主管")

# 按产品线配置审批
class dtdream_shenpi_by_product_line(models.Model):
    _name = "dtdream.shenpi.by.product.line"

    shenpi_by_product_line_id = fields.Many2one('dtdream.shenpi.config')
    zongbu_product_charge = fields.Many2one('hr.employee',string="总部产品经理")
    zongbu_service_charge = fields.Many2one('hr.employee',string="总部服务经理")
    categ_id = fields.Many2one('product.category',string="产品线")


# 销售审批配置类
class dtdream_shenpi_config(models.Model):
    _name = "dtdream.shenpi.config"

    name = fields.Char(default="销售审批配置")

    shenpi_product_line = fields.One2many('dtdream.shenpi.by.product.line','shenpi_by_product_line_id', string='销售产品线审批配置',copy=True)
    shenpi_line = fields.One2many('dtdream.shenpi.line','shenpi_line_id', string='销售部门审批配置',copy=True)
    business_interface_person = fields.Many2many('hr.employee',string="商务接口人")
    sales_manager = fields.Many2one('hr.employee',string="营销管理部部长")
    market_manager = fields.Many2one('hr.employee',string="市场部总裁")
    company_manager = fields.Many2one('hr.employee',string="公司总裁")
    sale_grant_discount = fields.Float(string="营销管理部授权折扣(%)")

    @api.onchange("sale_grant_discount")
    def _onchange_sale_discount(self):
        if self.sale_grant_discount > 100 or self.sale_grant_discount < 0:
            self.sale_grant_discount = ""
            warning = {
                    'title': '警告：',
                    'message': '授权折扣应在0%到100%之间',
                }
            return {'warning': warning}

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
