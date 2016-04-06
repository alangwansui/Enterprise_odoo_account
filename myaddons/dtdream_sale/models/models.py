# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 继承产品模型，修改字段
class dtdream_product(models.Model):
    _inherit = ["product.template"]

    bom = fields.Char(string="BOM",required=True)
    pro_status = fields.Selection([
        ('inPro', '生产'),
        ('outPro', '停产'),
    ])
    pro_type = fields.Many2one("product.pro.type", string="产品类别",required=True)

    pro_description = fields.Text(string="产品描述")
    ref_discount = fields.Float(string="参考折扣")
    pro_version = fields.Char(string="版本")
    remark = fields.Text(string="备注")
    office_manager_discount = fields.Float(string="办事处主任授权折扣")
    system_department_discount = fields.Float(string="系统部授权折扣")
    market_president_discount = fields.Float(string="市场部总裁授权折扣")

# 定义产品类别
class product_pro_type(models.Model):
    _name = 'product.pro.type'

    name = fields.Char('产品类别',required=True)

class res_users_read_access(models.Model):
    _inherit = 'res.users'

    user_access_industry = fields.Many2many("dtdream.industry", string="行业")
    user_access_office = fields.Many2many("dtdream.office", string="办事处")

    sale_res_team_id = fields.Many2many('crm.team',string='Sales Team')


class res_crm_team(models.Model):
    _inherit = 'crm.team'

    res_member_ids = fields.Many2many('res.users', 'sale_res_team_id', string='Team Members')


#定义办事处模型
class dtdream_office(models.Model):
    _name = 'dtdream.office'

    name = fields.Char("办事处名称",required=True)
    code = fields.Char("办事处编码",required=True)

class dtdream_product_line(models.Model):
    _name = 'dtdream.product.line'

    @api.depends('product_id')
    def _compute_fields(self):
        for rec in self:
            rec.bom = rec.product_id.bom
            rec.pro_type = rec.product_id.pro_type.name
            rec.pro_description = rec.product_id.pro_description
            rec.pro_name = rec.product_id.name
            rec.ref_discount = rec.product_id.ref_discount
            rec.list_price = rec.product_id.list_price

    product_line_id = fields.Many2one('crm.lead', string='产品', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.template', string='产品',ondelete='restrict', required=True,track_visibility='onchange')
    sequence = fields.Integer(string='Sequence', default=10)

    bom = fields.Char('BOM',compute=_compute_fields)
    pro_type = fields.Char('产品类别',compute=_compute_fields)
    pro_description = fields.Char('产品描述',compute=_compute_fields)
    pro_name = fields.Char('产品名称',compute=_compute_fields)
    list_price = fields.Float('目录价',compute=_compute_fields)
    ref_discount = fields.Float('参考折扣',compute=_compute_fields)
    apply_discount = fields.Float('申请折扣')
    pro_num = fields.Integer('数量')
    config_set = fields.Char('配置组')


    # def on_change_product_id(self, cr, uid, ids, product_id, context=None):
    #     values = {}
    #     product = self.pool.get('product.template').browse(cr, uid, product_id, context=context)
    #     if product_id:
    #         values = {
    #             'bom': product.bom,
    #             'pro_type': product.pro_type.name,
    #             'pro_description': product.pro_description,
    #             'pro_name': product.name,
    #             'ref_discount': product.ref_discount,
    #             'list_price':product.list_price
    #         }
    #     return {'value': values}

class dtdream_sale(models.Model):
    _inherit = 'crm.lead'

    @api.onchange('bidding_time','supply_time')
    def _onchange_time(self):
        if self.bidding_time!=False and self.supply_time!=False:
            if self.bidding_time >= self.supply_time:
                warning = {
                    'title': '警告：',
                    'message': '供货时间应晚于招标时间。',
                }
                return {'warning': warning}

    @api.onchange('pre_implementation_time','pre_check_time')
    def _onchange_time_pre(self):
        if self.pre_implementation_time!=False and self.pre_check_time!=False:
            if self.pre_implementation_time >= self.pre_check_time:
                warning = {
                    'title': '警告：',
                    'message': '预计验收时间应晚于预计开始实施时间。',
                }
                return {'warning': warning}

    @api.depends('product_line')
    def _onchange_product_line(self):
        list_price = 0
        ref_price = 0
        apply_price = 0
        for rec in self.product_line:
            list_price = list_price + rec.list_price * rec.pro_num
            ref_price = ref_price + rec.list_price * rec.pro_num * rec.ref_discount
            apply_price = apply_price + rec.list_price * rec.pro_num * rec.apply_discount
        self.total_list_price = list_price
        self.total_ref_price = ref_price
        self.total_apply_price = apply_price


    user_id = fields.Many2one(string="Salesperson")
    project_number = fields.Char(string="项目编号", default="New",store=True,readonly=True)
    project_leave = fields.Selection([
        ('company_leave', '公司级'),
        ('department_leave', '部门级'),
        ('normal_leave', '一般项目'),
    ],required=True)
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",required=True)
    industry_id = fields.Many2one("dtdream.industry", string="行业",required=True)
    office_id = fields.Many2one("dtdream.office", string="办事处",required=True)
    bidding_time = fields.Date("招标时间",required=True,default=datetime.today())
    supply_time = fields.Date("供货时间",required=True,default=datetime.today() + relativedelta(months=1))
    pre_implementation_time = fields.Date("预计开始实施时间",required=True,default=datetime.today()+ relativedelta(months=2))
    pre_check_time = fields.Date("预计验收时间",required=True,default=datetime.today() + relativedelta(months=3))
    sale_channel = fields.Char("渠道",required=True)
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    project_space = fields.Char('项目空间')
    partner_id = fields.Many2one(required=True)
    ali_division = fields.Selection([
        ('1','数据中国/部委事业部/金融/央企/其他'),
    ],'阿里对应事业部')
    ali_saleman = fields.Char('阿里对应销售')




    product_line = fields.One2many('dtdream.product.line', 'product_line_id', string='产品配置',copy=True)

    project_detail = fields.Text("项目详情")

    total_list_price = fields.Float('目录价总计',store=True,compute=_onchange_product_line)
    total_ref_price = fields.Float('参考折扣价总计',store=True,compute=_onchange_product_line)
    total_apply_price = fields.Float('申请折扣价总计',store=True,compute=_onchange_product_line)

    @api.onchange("system_department_id")
    def onchange_system_department(self):
        if self.system_department_id:
            return {
                'domain': {
                    "industry_id":[('parent_id','=',self.system_department_id.id)]
                }
            }

    @api.onchange("industry_id")
    def onchange_industry_id(self):
        if self.industry_id:
            self.system_department_id = self.industry_id.parent_id

    @api.model
    def create(self, vals):
        if vals.get('project_number', 'New') == 'New':
            o_id = vals.get('office_id')
            office_rec = self.env['dtdream.office'].search([('id','=',o_id)])
            vals['project_number'] = ''.join([office_rec.code,self.env['ir.sequence'].next_by_code('project.number'),'N']) or 'New'
        result = super(dtdream_sale, self).create(vals)
        return result

# 定义行业模型
class dtdream_industry(models.Model):
    _name = 'dtdream.industry'

    # @api.multi
    # def name_get(self):
    #     def get_names(cat):
    #         """ Return the list [cat.name, cat.parent_id.name, ...] """
    #         res = []
    #         while cat:
    #             res.append(cat.name)
    #             cat = cat.parent_id
    #         return res
    #     return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    name = fields.Char(string='行业名称',required=True)
    code = fields.Char(string='行业编码',required=True)
    parent_id = fields.Many2one('dtdream.industry', string='上级行业')
    children_ids = fields.One2many('dtdream.industry','parent_id',string='下级行业')