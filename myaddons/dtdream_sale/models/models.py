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
    company_president_discount = fields.Float(string="公司总裁授权折扣")

# 定义产品类别
class product_pro_type(models.Model):
    _name = 'product.pro.type'

    name = fields.Char('产品类别',required=True)

class res_users_read_access(models.Model):
    _inherit = ['res.users']

    user_access_industry = fields.Many2many("dtdream.industry", string="行业")
    user_access_office = fields.Many2many("dtdream.office", string="办事处")

#定义办事处模型
class dtdream_office(models.Model):
    _name = 'dtdream.office'

    name = fields.Char("办事处名称",required=True)
    code = fields.Char("办事处编码",required=True)

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

    user_id = fields.Many2one(string="项目责任人")
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

    partner_id = fields.Many2one(required=True)
    # child_ids = fields.One2many('res.partner', 'parent_id', 'Contacts', domain=[('active','=',True)])
    # partner_name = fields.Char(readonly=True)
    # email_form = fields.Char(readonly=True)
    # function = fields.Char(readonly=True)
    # phone = fields.Char(readonly=True)
    # mobile = fields.Char(readonly=True)


    project_detail = fields.Text("项目详情")

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