# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp .exceptions import ValidationError

# 继承产品模型，修改字段
class dtdream_product(models.Model):
    _inherit = ["product.template"]

    bom = fields.Char(string="BOM编码",required=True)
    pro_status = fields.Selection([
        ('inPro', '生产'),
        ('outPro', '停产'),
    ],required=True)
    pro_type = fields.Many2one("product.pro.type", string="产品类别",required=True)

    # pro_parent_id = fields.Many2one("product.template",string="上级BOM")
    pro_child_ids = fields.One2many('dtdream.child.product.line', 'child_product_id', string='下级BOM',copy=True)
    pro_description = fields.Text(string="产品对内中文描述")
    pro_description_out = fields.Text(string="产品对外中文描述",required=True)
    effect_time = fields.Date("生效日期",required=True,default=lambda self:datetime.now())
    ref_discount = fields.Float(string="参考折扣(%)",required=True)
    pro_version = fields.Char(string="版本")
    remark = fields.Text(string="备注")
    office_manager_discount = fields.Float(string="办事处主任折扣(%)",required=True)
    system_department_discount = fields.Float(string="系统部折扣(%)",required=True)
    market_president_discount = fields.Float(string="市场部总裁折扣(%)",required=True)
    sale_grant_discount = fields.Float(string="营销管理部折扣(%)",required=True)
    is_temporary_bom = fields.Selection([
        ('1','是'),
        ('2','否'),
    ],string="是否临时BOM",default="2")
    list_price = fields.Integer(string="目录价",required=True)
    cost_price = fields.Integer(string="成本价",required=True)
    pro_num = fields.Integer(string="数量")
    pro_source = fields.Selection([
        ('1','自研'),
        ('2','外购'),
    ],string="来源",required=True)

    @api.onchange("list_price")
    def _onchange_list_price(self):
        if self.list_price < 0:
            self.list_price = ""
            warning = {
                    'title': '警告：',
                    'message': '目录价不能小于0',
                }
            return {'warning': warning}

    @api.onchange("ref_discount")
    def _onchange_ref_discount(self):
        if self.ref_discount > 100 or self.ref_discount < 0:
            self.ref_discount = ""
            warning = {
                    'title': '警告：',
                    'message': '参考折扣应应在0%到100%之间',
                }
            return {'warning': warning}

    @api.onchange('office_manager_discount')
    def _onchange_office_manager_discount(self):
        if self.office_manager_discount > 100 or self.office_manager_discount < 0:
            self.office_manager_discount = "";
            warning = {
                    'title': '警告：',
                    'message': '办事处主任折扣应在0%到100%之间',
                }
            return {'warning': warning}

    @api.onchange('system_department_discount')
    def _onchange_system_department_discount(self):
        if self.system_department_discount > 100 or self.system_department_discount < 0:
            self.system_department_discount = "";
            warning = {
                    'title': '警告：',
                    'message': '系统部折扣应在0%到100%之间',
                }
            return {'warning': warning}

    @api.onchange('market_president_discount')
    def _onchange_market_president_discount(self):
        if self.market_president_discount > 100 or self.market_president_discount < 0:
            self.market_president_discount = "";
            warning = {
                    'title': '警告：',
                    'message': '市场部总裁折扣应大于0%且小于100%',
                }
            return {'warning': warning}

# 定义产品类别
class product_pro_type(models.Model):
    _name = 'product.pro.type'

    name = fields.Char('产品类别',required=True)

class res_users_read_access(models.Model):
    _inherit = 'res.users'

    user_access_industry = fields.Many2many("dtdream.industry", string="行业")
    user_access_office = fields.Many2many("dtdream.office", string="办事处")
    user_access_product_type = fields.Many2many("product.category", string="产品分类")
    user_access_department = fields.Many2many("hr.department",string="部门")

    sale_res_team_id = fields.Many2many('crm.team',string='Sales Team')

    def _get_company(self,cr, uid, context=None, uid2=False):
        if not uid2:
            uid2 = uid
        # Use read() to compute default company, and pass load=_classic_write to
        # avoid useless name_get() calls. This will avoid prefetching fields
        # while computing default values for new db columns, as the
        # db backend may not be fully initialized yet.
        user_data = self.pool['res.users'].read(cr, uid, uid2, ['company_id'],
                                                context=context, load='_classic_write')
        comp_id = user_data['company_id']
        return comp_id or False

    def _get_companies(self, cr, uid, context=None):
        c = self._get_company(cr, uid, context)
        if c:
            return [c]
        return False

    def _get_group(self,cr, uid, context=None):
        dataobj = self.pool.get('ir.model.data')
        result = []
        try:
            dummy,group_id = dataobj.get_object_reference(cr, 1, 'base', 'group_user')
            result.append(group_id)
            # dummy,group_id = dataobj.get_object_reference(cr, 1, 'base', 'group_partner_manager')
            # result.append(group_id)
        except ValueError:
            # If these groups does not exists anymore
            pass
        return result

    _defaults = {
        'password': '',
        'active': True,
        'customer': False,
        'company_id': _get_company,
        'company_ids': _get_companies,
        'groups_id': _get_group,
    }


class res_crm_team(models.Model):
    _inherit = 'crm.team'

    res_member_ids = fields.Many2many('res.users', 'sale_res_team_id', string='Team Members')

    _defaults = {
        'stage_ids': "",
        'use_opportunities': True,
        'use_leads': True,
    }

    def action_your_pipeline(self, cr, uid, context=None):
        IrModelData = self.pool['ir.model.data']
        action = IrModelData.xmlid_to_object(cr, uid, 'crm.crm_lead_opportunities_tree_view', context=context).read(['name', 'help', 'res_model', 'target', 'domain', 'context', 'type', 'search_view_id'])
        if not action:
            action = {}
        else:
            action = action[0]

        user_team_id = self.pool['res.users'].browse(cr, uid, uid, context=context).sale_team_id.id
        if not user_team_id:
            user_team_id = self.search(cr, uid, [], context=context, limit=1)
            user_team_id = user_team_id and user_team_id[0] or False
            action['help'] = """<p class='oe_view_nocontent_create'>Click here to add new opportunities</p><p>
    Looks like you are not a member of a sales team. You should add yourself
    as a member of one of the sales team.
</p>"""
            if user_team_id:
                action['help'] += "<p>As you don't belong to any sales team, Odoo opens the first one by default.</p>"

        action_context = eval(action['context'], {'uid': uid})
        # if user_team_id:
        #     action_context.update({
        #         'default_team_id': user_team_id,
        #         'search_default_team_id': user_team_id
        #     })

        tree_view_id = IrModelData.xmlid_to_res_id(cr, uid, 'crm.crm_case_tree_view_oppor')
        form_view_id = IrModelData.xmlid_to_res_id(cr, uid, 'crm.crm_case_form_view_oppor')
        kanb_view_id = IrModelData.xmlid_to_res_id(cr, uid, 'crm.crm_case_kanban_view_leads')
        action.update({
            'views': [
                [tree_view_id, 'tree'],
                [kanb_view_id, 'kanban'],
                [form_view_id, 'form'],
                [False, 'graph'],
                [False, 'calendar'],
                [False, 'pivot']
            ],
            'context': action_context,
        })
        return action


#定义办事处模型
class dtdream_office(models.Model):
    _name = 'dtdream.office'

    name = fields.Char("办事处名称",required=True)
    code = fields.Char("办事处编码",required=True)

class dtdream_product_line(models.Model):
    _name = 'dtdream.product.line'

    product_line_id = fields.Many2one('crm.lead', string='产品', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.template', string='产品',ondelete='restrict',track_visibility='onchange')

    bom = fields.Char('BOM')
    pro_type = fields.Char('产品类别')
    pro_description = fields.Char('产品描述')
    pro_name = fields.Char('产品型号')
    list_price = fields.Float('目录价')
    ref_discount = fields.Float('参考折扣(%)')
    apply_discount = fields.Float('申请折扣(%)')
    pro_num = fields.Integer('数量')
    config_set = fields.Char('发货地')

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id.id:
                rec.bom = rec.product_id.bom
                rec.pro_type = rec.product_id.pro_type.name
                rec.pro_description = rec.product_id.pro_description
                rec.pro_name = rec.product_id.name
                rec.ref_discount = rec.product_id.ref_discount
                rec.list_price = rec.product_id.list_price

    @api.model
    def create(self, vals):
        if vals.has_key('product_id'):
            if vals['product_id']:
                rec = self.product_id.search([('id','=',vals['product_id'])])[0]
                vals['bom'] = rec.bom
                vals['pro_type'] = rec.pro_type.name
                vals['pro_description'] = rec.pro_description
                vals['pro_name'] = rec.name
                vals['list_price'] = rec.list_price
                vals['ref_discount'] = rec.ref_discount
                vals['product_id'] = None
        result = super(dtdream_product_line, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        if vals.has_key('product_id'):
            if vals['product_id']:
                rec = self.product_id.search([('id','=',vals['product_id'])])[0]
                vals['bom'] = rec.bom
                vals['pro_type'] = rec.pro_type.name
                vals['pro_description'] = rec.pro_description
                vals['pro_name'] = rec.name
                vals['list_price'] = rec.list_price
                vals['ref_discount'] = rec.ref_discount
                vals['product_id'] = None
        result = super(dtdream_product_line, self).write(vals)
        return result

    @api.onchange("pro_num")
    def _onchange_pro_num(self):
        if self.pro_num < 0:
            self.pro_num = ""
            warning = {
                    'title': '警告：',
                    'message': '数量不能小于0',
                }
            return {'warning': warning}

    @api.onchange("apply_discount")
    def _onchange_apply_discount(self):
        if self.apply_discount > 100 or self.apply_discount < 0:
            self.apply_discount = ""
            warning = {
                    'title': '警告：',
                    'message': '参考折扣应在0%到100%之间',
                }
            return {'warning': warning}

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

    @api.model
    def crm_lead_won_action(self,record_id):
        if type(record_id) == list:
            record_id = record_id[0]
        view_id = self.env.ref('dtdream_sale.crm_lead_won_view_form').id,
        action = {
                'name': '项目中标',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'crm.lead',
                'target':'new',
                'res_id': record_id,
                'context': self._context,
                }
        return action

    @api.depends('partner_id')
    def _compute_partner_fields(self):
        i = 1
        if self.partner_id.child_ids:
            self.dt_mobile = self.partner_id.mobile
        else :
            self.dt_mobile = self.partner_id.mobile
            self.dt_contact_name = self.partner_id.name
        if self.partner_id.company_type == "person":
            self.dt_partner_name = self.partner_id.parent_id.name
        else:
            self.dt_partner_name = ""

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
            ref_price = ref_price + rec.list_price * rec.pro_num * rec.ref_discount * 0.01
            apply_price = apply_price + rec.list_price * rec.pro_num * rec.apply_discount * 0.01
        self.total_list_price = list_price
        self.total_ref_price = ref_price
        self.total_apply_price = apply_price

    @api.depends('project_space')
    def _onchange_project_space(self):
        for recc in self:
            space_total = 0
            bidding_space_total = 0
            for rec in recc.project_space:
                space_total = space_total + rec.project_space
                bidding_space_total = bidding_space_total + rec.bidding_space
            recc.space_total = space_total
            recc.bidding_space_total = bidding_space_total

    @api.onchange('sale_apply_id')
    def _onchange_sale_apply_uid(self):
        self.sale_apply_id_uid = self.sale_apply_id.env['res.users'].search([('login','=',self.sale_apply_id.login)]).id

    # @api.onchange('is_invest_project')
    # def _onchange_invesr(self):
    #     if self.is_invest_project == True:
    #
    #     else:

    @api.one
    def _compute_software_space(self):
        software_space = 0
        for rec in self.project_space:
            software_space = software_space + rec.software_space
        self.software_space = software_space

    description = fields.Text('项目进展')

    name = fields.Char('项目名称',required=True,select=1,track_visibility='onchange',size=64)
    user_id = fields.Many2one(string="Salesperson")
    project_number = fields.Char(string="项目编号", default="New",store=True,readonly=True)
    project_leave = fields.Selection([
        ('company_leave', '公司级'),
        ('department_leave', '部门级'),
        ('normal_leave', '一般项目'),
    ],required=True,track_visibility='onchange',string="项目级别")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",required=True,track_visibility='onchange')
    industry_id = fields.Many2one("dtdream.industry", string="行业",required=True,track_visibility='onchange')
    office_id = fields.Many2one("dtdream.office", string="办事处",required=True,track_visibility='onchange')
    bidding_time = fields.Date("招标时间",required=True,default=lambda self:datetime.now(),track_visibility='onchange')
    supply_time = fields.Date("供货时间",required=True,default=lambda self:(datetime.now() + relativedelta(months=1)),track_visibility='onchange')
    pre_implementation_time = fields.Date("预计开始实施时间",default=lambda self:(datetime.now() + relativedelta(months=2)))
    pre_check_time = fields.Date("预计验收时间",default=lambda self:(datetime.now() + relativedelta(months=3)))
    sale_channel = fields.Char("渠道",required=True,track_visibility='onchange')
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度',required=True,track_visibility='onchange')
    project_space = fields.One2many('dtdream.project.space.line', 'project_line_id', string='项目空间',copy=True)
    software_space = fields.Float('软件空间(万元)',digits=(16,0),compute=_compute_software_space)
    partner_id = fields.Many2one(required=True,track_visibility='onchange')
    ali_division = fields.Selection([
        ('1','数据中国'),
        ('2','部委事业部'),
        ('3','央企'),
        ('4','民企'),
        ('5','金融'),
        ('6','互联网+'),
        ('7','大安全部'),
        ('8','中间件部'),
        ('9','支付宝'),
        ('10','无'),
    ],'阿里对应事业部')
    is_project_budget = fields.Selection([
        ('1', '是'),
        ('0', '否'),
    ],string='项目是否有预算',required=True,track_visibility='onchange')
    ali_saleman = fields.Char('阿里对应销售')
    is_dtdream_integrated = fields.Selection([
        ('1', '是'),
        ('0', '否'),
    ],string='是否数梦集成项目',required=True,track_visibility='onchange')
    is_invest_project = fields.Selection([
        ('1', '是'),
        ('0', '否'),
    ],string='是否投资类项目',required=True,track_visibility='onchange')

    @api.onchange("project_province_new")
    def onchange_project_province_new(self):
        if self.project_province_new:
            if self.project_place_new.parent_id != self.project_province_new:
                self.project_place_new = ""
            return {
                'domain': {
                    "project_place_new":[('parent_id','=',self.project_province_new.id)]
                }
            }

    @api.onchange("project_place_new")
    def onchange_project_place_new(self):
        if self.project_place_new:
            self.project_province_new = self.project_place_new.parent_id
            if self.project_country.parent_id != self.project_place_new:
                self.project_country = ""
            return {
                'domain': {
                    "project_country":[('parent_id','=',self.project_place_new.id)]
                }
            }

    @api.onchange("project_country")
    def onchange_project_country(self):
        if self.project_country:
            self.project_place_new = self.project_country.parent_id
            self.project_province_new = self.project_country.parent_id.parent_id

    project_province_new = fields.Many2one("dtdream.area", '省份',required=True,domain=[('parent_id','=',False)],track_visibility='onchange')

    product_category_type_id = fields.Many2many("product.category", string="产品分类")
    project_place_new = fields.Many2one("dtdream.area", '城市',required=True,domain=[('parent_id.parent_id','=',False)],track_visibility='onchange')
    project_country = fields.Many2one("dtdream.area", '区县',domain=[('parent_id.parent_id.parent_id','=',False)],track_visibility='onchange')
    sale_apply_id = fields.Many2one("hr.employee",string="营销责任人",required=True,track_visibility='onchange')
    sale_apply_id_uid = fields.Integer(string="营销责任人id")

    product_line = fields.One2many('dtdream.product.line', 'product_line_id', string='产品配置',copy=True)

    project_detail = fields.Text("项目详情",required=True,track_visibility='onchange')

    total_list_price = fields.Float('目录价总计',store=True,compute=_onchange_product_line)
    total_ref_price = fields.Float('参考折扣价总计',store=True,compute=_onchange_product_line)
    total_apply_price = fields.Float('申请折扣价总计',store=True,compute=_onchange_product_line)
    space_total = fields.Float('合计(万元)',store=True,compute=_onchange_project_space,digits=(16,0))
    bidding_space_total = fields.Float('中标金额合计(万元)',store=True,compute=_onchange_project_space,digits=(16,0))

    dt_partner_name = fields.Char(compute=_compute_partner_fields,store=True,string="公司名称")
    dt_contact_name = fields.Char(compute=_compute_partner_fields,store=True,string="联系人名称")
    dt_mobile = fields.Char(compute=_compute_partner_fields,store=True,string="手机")
    des_records = fields.One2many("dtdream.des.records","des_id",string="进展记录")

    stage_id = fields.Many2one('crm.stage', string='Stage', track_visibility='onchange', select=True)

    is_red = fields.Boolean(string="判断招标时间是否早于当天")

    pro_background = fields.Text("投资类项目背景")

    categ_id_parent = fields.Many2one('product.category',string="产品一级分类",related='project_space.categ_id_parent',store=True,dtdream_groupable=True)

    categ_id = fields.Many2one('product.category',string="产品二级分类",related='project_space.categ_id',store=True)

    is_lost = fields.Boolean(string="已丢单",default=False)
    is_won = fields.Boolean(string="已中标",default=False)
    is_important = fields.Boolean(string="重点项目",default=False)

    bidding_channel = fields.Char(string="中标渠道")
    if_zhitou = fields.Boolean(string="是否直投")

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
                # if col_name != "user_id":
                tracking = self.env['mail.tracking.value'].create_tracking_values(initial_value, new_value, col_name, col_info)
                if tracking and col_name != "user_id":
                    tracking_value_ids.append([0, 0, tracking])
                if col_name in tracked_fields and col_name != "user_id":
                    changes.add(col_name)
        return changes, tracking_value_ids

    @api.constrains("name")
    def check_name(self):
        if len(self.search([('name','=',self.name)])) > 1:
            raise ValidationError("项目名称已存在。")

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

    @api.model
    def create(self, vals):
        if len(vals.get('des_records',"")) == 0 :
            raise ValidationError("请录入项目进展")
        if len(vals.get('project_space',"")) == 0 :
            raise ValidationError("请录入项目空间")
        if vals.get('project_number', 'New') == 'New':
            o_id = vals.get('office_id')
            office_rec = self.env['dtdream.office'].search([('id','=',o_id)])
            num = len(self.search([('create_date','like',(datetime.now().strftime('%Y-%m-%d')+"%")),('office_id','=',o_id)]))+1
            if len(self.search([('create_date','like',(datetime.now().strftime('%Y-%m-%d')+"%")),('office_id','=',o_id)], order="id desc"))>0:
                num = int(self.search([('create_date','like',(datetime.now().strftime('%Y-%m-%d')+"%")),('office_id','=',o_id)], order="id desc")[0].project_number[-3:-1])+1
            if num < 10:
                num = "%02d"%num
            if vals.get('project_leave') == "company_leave":
                vals['project_number'] = ''.join([office_rec.code,datetime.now().strftime('%Y%m%d'),num,'A']) or 'New'
            if vals.get('project_leave') == "department_leave":
                vals['project_number'] = ''.join([office_rec.code,datetime.now().strftime('%Y%m%d'),num,'B']) or 'New'
            if vals.get('project_leave') == "normal_leave":
                vals['project_number'] = ''.join([office_rec.code,datetime.now().strftime('%Y%m%d'),num,'N']) or 'New'
        result = super(dtdream_sale, self).create(vals)
        result.write({"product_category_type_id": [(6,0,[])]})
        if vals.has_key('project_space'):
            for project_space in vals['project_space']:
                result.write({"product_category_type_id": [(4,[project_space[2]['categ_id']])]})
        return result

    def stage_find(self, cr, uid, cases, team_id, domain=None, order='sequence', context=None):
        if context is None:
            context = {}
        search_domain = []
        stage_ids = self.pool.get('crm.stage').search(cr, uid, search_domain, order=order, limit=1, context=context)
        if stage_ids:
            return stage_ids[0]
        return False

    def onchange_stage_id(self, cr, uid, ids, stage_id, context=None):
        if not stage_id:
            return {'value': {}}
        stage = self.pool['crm.stage'].browse(cr, uid, stage_id, context=context)
        if not stage.on_change:
            return {'value': {}}
        return {'value': {'probability': stage.probability}}

    @api.multi
    def write(self, vals):
        if vals.has_key('project_leave'):
            if vals.get('project_leave') == "company_leave":
                vals['project_number'] = self.project_number[:-1]+"A"
                self.project_number = self.project_number[:-1]+"A"
            if vals.get('project_leave') == "department_leave":
                vals['project_number'] = self.project_number[:-1]+"B"
                self.project_number = self.project_number[:-1]+"B"
            if vals.get('project_leave') == "normal_leave":
                vals['project_number'] = self.project_number[:-1]+"N"
                self.project_number = self.project_number[:-1]+"N"
        if vals.has_key('stage_id') and self.sale_apply_id.user_id.id != self._uid and not self.user_has_groups('dtdream_sale.group_dtdream_sale_manager'):
            raise ValidationError("只有项目的营销责任人可以拖动项目改变项目状态。")
        if vals.has_key('stage_id'):
            if self.env['crm.stage'].search([('id','=',vals.get('stage_id'))]).name == u"机会点":
                self.type = "lead"
            else :
                self.type = "opportunity"
            if self.env['crm.stage'].search([('id','=',vals.get('stage_id'))]).name == u"丢单":
                self.is_lost = True
            else:
                self.is_lost = False
            if self.stage_id.name == u"丢单":
                if self.user_has_groups('dtdream_sale.group_dtdream_sale_manager'):
                    self.is_lost = False
                else:
                    raise ValidationError('只有项目管理员可改变状态为"丢单"的项目。')
            if self.env['crm.stage'].search([('id','=',vals.get('stage_id'))]).name == u"中标":
                self.is_won = True
                for rec in self.project_space:
                    rec.view_bidding_space = True
            else:
                self.is_won = False
                for rec in self.project_space:
                    rec.view_bidding_space = False
            if self.stage_id.name == u"中标" :
                if self.user_has_groups('dtdream_sale.group_dtdream_sale_manager'):
                    self.is_won = False
                else:
                    raise ValidationError('只有项目管理员可改变状态为"中标"项目。')
        if vals.has_key('des_records') and vals.get('des_records')[0][0]==2 :
            raise ValidationError("请录入项目进展")
        if vals.has_key('project_space') and vals.get('project_space')[0][0]==2 :
            raise ValidationError("请录入项目空间")
        if vals.has_key('description'):
            self.env['dtdream.des.records'].create({"name":self.description,"des_id":self.id})
        result = super(dtdream_sale, self).write(vals)
        if vals.has_key('project_space'):
            rec = self.env['crm.lead'].search([('id','=',self.id)])
            rec.write({"product_category_type_id": [(6,0,[])]})
            for project_space in rec.project_space:
                rec.write({"product_category_type_id": [(4,project_space.categ_id.id)]})
        return result

    def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        access_rights_uid = access_rights_uid or uid
        stage_obj = self.pool.get('crm.stage')
        order = stage_obj._order
        # lame hack to allow reverting search, should just work in the trivial case
        if read_group_order == 'stage_id desc':
            order = "%s desc" % order
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', 'ids'): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        search_domain = []
        type = self._resolve_type_from_context(cr, uid, context=context)
        if type:
            search_domain += ['|', ('type', '=', type), ('type', '=', 'both')]
        # perform search
        stage_ids = stage_obj._search(cr, uid, search_domain, order=order, access_rights_uid=access_rights_uid, context=context)
        result = stage_obj.name_get(cr, access_rights_uid, stage_ids, context=context)
        # restore order of the search
        result.sort(lambda x, y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))

        fold = {}
        for stage in stage_obj.browse(cr, access_rights_uid, stage_ids, context=context):
            fold[stage.id] = stage.fold or False
        return result, fold

    _group_by_full = {
        'stage_id': _read_group_stage_ids
    }

    def res_allocate_salesman(self, cr, uid, ids, user_ids=None, team_id=False,sale_apply_id=False, context=None):
        """
        Assign salesmen and salesteam to a batch of leads.  If there are more
        leads than salesmen, these salesmen will be assigned in round-robin.
        E.g.: 4 salesmen (S1, S2, S3, S4) for 6 leads (L1, L2, ... L6).  They
        will be assigned as followed: L1 - S1, L2 - S2, L3 - S3, L4 - S4,
        L5 - S1, L6 - S2.

        :param list ids: leads/opportunities ids to process
        :param list user_ids: salesmen to assign
        :param int team_id: salesteam to assign
        :return bool
        """
        index = 0

        for lead_id in ids:
            value = {}
            if team_id:
                value['team_id'] = team_id
            if sale_apply_id:
                value['sale_apply_id'] = sale_apply_id
            if user_ids:
                value['user_id'] = user_ids[index]
                # Cycle through user_ids
                index = (index + 1) % len(user_ids)
            if value:
                self.write(cr, uid, [lead_id], value, context=context)
        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # for rec in self.search([]):
        #     if rec.bidding_time < datetime.now().strftime('%Y-%m-%d'):
        #         rec.is_red = True
        #     else:
        #         rec.is_red = False
        result = super(dtdream_sale, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        return result

    # @api.model
    # def if_hide(self):
    #     if self.env.user.has_group('dtdream_sale.group_dtdream_sale_high_manager'):
    #         return False
    #     return True

    def action_set_lost(self, cr, uid, ids, context=None):
        if len(self.pool.get('crm.stage').search(cr,uid,[('name','=',u'丢单')])) > 0:
            stage_lost_id = self.pool.get('crm.stage').search(cr,uid,[('name','=',u'丢单')])[0]
        else:
             raise ValidationError('尚未添加"丢单"阶段，请联系项目管理员添加。')
        if self.browse(cr, uid,int(context['active_id']), context=context).lost_reason.name == u"重复录入":
            return self.write(cr, uid, ids, {'probability': 0,'active': False,'stage_id': stage_lost_id,'is_lost':True}, context=context)
        else:
            return self.write(cr, uid, ids, {'stage_id': stage_lost_id,'is_lost':True}, context=context)

    @api.multi
    def action_won_apply(self):
        if not self.bidding_channel:
            raise ValidationError('请填写中标渠道。')
        for rec in self.project_space:
            if not rec.bidding_space or rec.bidding_space == 0:
                raise ValidationError('请填写中标金额。')
        if len(self.env['crm.stage'].search([('name','=',u'中标')])) > 0:
            stage_won_id = self.env['crm.stage'].search([('name','=',u'中标')])[0].id
        else:
            raise ValidationError('尚未添加"中标"阶段，请联系项目管理员添加。')
        return self.write({'stage_id': stage_won_id})

    @api.model
    def action_set_other_stage(self,stage_name,rec_id):
        record = self.env['crm.stage'].search([('name','=',stage_name)])
        if len(record) > 0 :
            stage_id = record[0].id
            rec = self.search([('id','=',int(rec_id))])
            rec.write({'stage_id': stage_id})

    def action_set_important(self, cr, uid, ids, context=None):
        self.write(cr, uid,ids, {'is_important': True}, context=context)

    def action_cancel_important(self, cr, uid, ids, context=None):
        self.write(cr, uid,ids, {'is_important': False}, context=context)

# 定义行业模型
class dtdream_industry(models.Model):
    _name = 'dtdream.industry'

    name = fields.Char(string='系统部/行业名称',required=True)
    code = fields.Char(string='系统部/行业编码',required=True)
    parent_id = fields.Many2one('dtdream.industry', string='上级系统部/行业')

    children_ids = fields.One2many('dtdream.industry','parent_id',string='下级系统部/行业')

class dtdream_crm_partner_binding(models.Model):
    _inherit = 'crm.lead2opportunity.partner'

    name = fields.Selection([
                ('convert', 'Convert to opportunity')
            ],string='Conversion Action', required=True)
    sale_apply_id = fields.Many2one("hr.employee",string="营销责任人",required=True)
    action = fields.Selection([
                ('exist', 'Link to an existing customer'),
            ]
    )

    def default_get(self, cr, uid, fields, context=None):
        """
        Default get for name, opportunity_ids.
        If there is an exisitng partner link to the lead, find all existing
        opportunities links with this partner to merge all information together
        """
        lead_obj = self.pool.get('crm.lead')

        res = super(dtdream_crm_partner_binding, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            tomerge = [int(context['active_id'])]

            partner_id = res.get('partner_id')
            lead = lead_obj.browse(cr, uid, int(context['active_id']), context=context)
            email = lead.partner_id and lead.partner_id.email or lead.email_from

            tomerge.extend(self._get_duplicated_leads(cr, uid, partner_id, email, include_lost=True, context=context))
            tomerge = list(set(tomerge))

            if 'action' in fields and not res.get('action'):
                res.update({'action' : partner_id and 'exist' or 'create'})
            if 'partner_id' in fields:
                res.update({'partner_id' : partner_id})
            if 'name' in fields:
                res.update({'name' : 'convert'})
            if 'opportunity_ids' in fields and len(tomerge) >= 2:
                res.update({'opportunity_ids': tomerge})
            if lead.user_id:
                res.update({'sale_apply_id': lead.sale_apply_id.id})
            if lead.team_id:
                res.update({'team_id': lead.team_id.id})
            if not partner_id and not lead.contact_name:
                res.update({'action': 'nothing'})
        return res

    def action_apply(self, cr, uid, ids, context=None):
        """
        Convert lead to opportunity or merge lead and opportunity and open
        the freshly created opportunity view.
        """
        if context is None:
            context = {}

        lead_obj = self.pool['crm.lead']
        partner_obj = self.pool['res.partner']

        w = self.browse(cr, uid, ids, context=context)[0]
        opp_ids = [o.id for o in w.opportunity_ids]
        vals = {
            'team_id': w.team_id.id,
            'sale_apply_id': w.sale_apply_id.id
        }
        if w.partner_id:
            vals['partner_id'] = w.partner_id.id
        if w.name == 'merge':
            lead_id = lead_obj.merge_opportunity(cr, uid, opp_ids, context=context)
            lead_ids = [lead_id]
            lead = lead_obj.read(cr, uid, lead_id, ['type', 'user_id'], context=context)
            if lead['type'] == "lead":
                context = dict(context, active_ids=lead_ids)
                vals.update({'lead_ids': lead_ids, 'user_ids': [w.user_id.id]})
                self._convert_opportunity(cr, uid, ids, vals, context=context)
            elif not context.get('no_force_assignation') or not lead['user_id']:
                vals.update({'user_id': w.user_id.id})
                lead_obj.write(cr, uid, lead_id, vals, context=context)
        else:
            lead_ids = context.get('active_ids', [])
            vals.update({'lead_ids': lead_ids, 'user_ids': [w.user_id.id]})
            self._convert_opportunity(cr, uid, ids, vals, context=context)
            for lead in lead_obj.browse(cr, uid, lead_ids, context=context):
                if lead.partner_id and lead.partner_id.user_id != lead.user_id:
                    partner_obj.write(cr, uid, [lead.partner_id.id], {'user_id': lead.user_id.id}, context=context)

        return self.pool.get('crm.lead').redirect_opportunity_view(cr, uid, lead_ids[0], context=context)

    def _convert_opportunity(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        lead = self.pool.get('crm.lead')
        res = False
        lead_ids = vals.get('lead_ids', [])
        team_id = vals.get('team_id', False)
        sale_apply_id = vals.get('sale_apply_id', False)
        partner_id = vals.get('partner_id')
        data = self.browse(cr, uid, ids, context=context)[0]
        leads = lead.browse(cr, uid, lead_ids, context=context)
        for lead_id in leads:
            partner_id = self._create_partner(cr, uid, lead_id.id, data.action, partner_id or lead_id.partner_id.id, context=context)
            res = lead.convert_opportunity(cr, uid, [lead_id.id], partner_id, [], False, context=context)
        user_ids = vals.get('user_ids', False)
        if context.get('no_force_assignation'):
            leads_to_allocate = [lead_id.id for lead_id in leads if not lead_id.user_id]
        else:
            leads_to_allocate = lead_ids
        if user_ids:
            lead.res_allocate_salesman(cr, uid, leads_to_allocate, user_ids, team_id=team_id,sale_apply_id=sale_apply_id,context=context)
        return res

class dtdream_child_product_line(models.Model):
    _name = 'dtdream.child.product.line'

    @api.depends('dtdream_child_product_id')
    def _compute_child_fields(self):
        for rec in self:
            rec.child_bom = rec.dtdream_child_product_id.bom
            rec.child_pro_type = rec.dtdream_child_product_id.pro_type.name
            rec.child_categ_id = rec.dtdream_child_product_id.categ_id.name
            rec.child_pro_description_out = rec.dtdream_child_product_id.pro_description_out
            if rec.dtdream_child_product_id.is_temporary_bom:
                rec.child_is_temporary_bom = dict(rec.dtdream_child_product_id._columns['is_temporary_bom'].selection)[rec.dtdream_child_product_id.is_temporary_bom]
            if rec.dtdream_child_product_id.pro_status:
                rec.child_pro_status = dict(rec.dtdream_child_product_id._columns['pro_status'].selection)[rec.dtdream_child_product_id.pro_status]
            rec.child_effect_time = rec.dtdream_child_product_id.effect_time
            rec.child_write_uid = rec.dtdream_child_product_id.write_uid.name
            rec.child_write_date = rec.dtdream_child_product_id.write_date

    child_product_id = fields.Many2one('product.template', string='产品', ondelete='cascade', index=True, copy=False)
    dtdream_child_product_id = fields.Many2one('product.template', string='产品',ondelete='restrict', required=True,track_visibility='onchange')
    child_bom = fields.Char('BOM',compute=_compute_child_fields)
    child_pro_type = fields.Char('产品类别',compute=_compute_child_fields)
    child_categ_id = fields.Char('产品分类',compute=_compute_child_fields)
    child_pro_description_out = fields.Char('产品对外中文描述',compute=_compute_child_fields)
    child_is_temporary_bom = fields.Char('是否临时BOM',compute=_compute_child_fields)
    child_pro_status = fields.Char('状态',compute=_compute_child_fields)
    child_effect_time = fields.Char('生效日期',compute=_compute_child_fields)
    child_write_uid = fields.Char('最后更新人',compute=_compute_child_fields)
    child_write_date = fields.Char('最后更新时间',compute=_compute_child_fields)
    child_pro_num = fields.Integer('数量')
    @api.onchange("child_pro_num")
    def _onchange_pro_num(self):
        if self.child_pro_num < 0:
            self.child_pro_num = ""
            warning = {
                    'title': '警告：',
                    'message': '数量不能小于0',
                }
            return {'warning': warning}

class dtdream_project_space_line(models.Model):
    _name = "dtdream.project.space.line"

    project_line_id = fields.Many2one('crm.lead',string="关联到项目")

    # categ_id = fields.Many2one('product.category',string="产品分类")
    categ_id_parent = fields.Many2one('product.category',string="产品一级分类",domain="[('parent_id','=',False)]",required=True)
    categ_id = fields.Many2one('product.category',string="产品二级分类",domain="[('parent_id.parent_id','=',False)]",required=True)

    @api.onchange("categ_id_parent")
    def onchange_categ_id_parent(self):
        if self.categ_id_parent:
            if self.categ_id.parent_id != self.categ_id_parent:
                self.categ_id = ""
            return {
                'domain': {
                    "categ_id":[('parent_id','=',self.categ_id_parent.id)]
                }
            }

    @api.onchange("categ_id")
    def onchange_categ_id(self):
        if self.categ_id:
            self.categ_id_parent = self.categ_id.parent_id
        else:
            return {
                'domain': {
                    "categ_id":[('parent_id.parent_id','=',False)]
                }
            }

    @api.onchange("project_space")
    def _onchange_project_space(self):
        if self.project_space < 0:
            self.project_space = 0
            return {'warning': {
                "title": u"提示",
                "message": u"项目空间不能小于0"
            }}
        if self.project_space < self.software_space:
            self.project_space = 0
            return {'warning': {
                "title": u"提示",
                "message": u"软件空间必须小于项目空间"
            }}

    @api.onchange("software_space")
    def _onchange_software_space(self):
        if self.software_space < 0:
            self.software_space = 0
            return {'warning': {
                "title": u"提示",
                "message": u"软件空间不能小于0"
            }}
        if self.project_space < self.software_space:
            self.software_space = 0
            return {'warning': {
                "title": u"提示",
                "message": u"软件空间必须小于项目空间"
            }}

    software_space = fields.Float('软件空间(万元)',digits=(16,0))
    project_space = fields.Float('项目空间(万元)',digits=(16,0))
    bidding_space = fields.Float('中标金额(万元)',digits=(16,0))
    view_bidding_space = fields.Boolean(string="是否显示中标金额")

class dtdream_product_category(models.Model):
    _inherit = "product.category"

    @api.multi
    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            return cat.name
        return [(cat.id,get_names(cat)) for cat in self]


# 进展记录
class dtdream_des_records(models.Model):
    _name = "dtdream.des.records"
    _order = "id desc"

    name = fields.Text("项目进展")
    des_id = fields.Many2one("crm.lead",string="项目")
    week = fields.Integer(string="周别")

class DtdreamCrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    lead_id = fields.Many2one(ondelete="cascade")

# 定义区域
class dtdream_area(models.Model):
    _name = 'dtdream.area'

    child_ids = fields.One2many('dtdream.area', 'parent_id')
    name = fields.Char(string='区划名称',required=True)
    code = fields.Char(string='行政代号',required=True)
    parent_code = fields.Char(string='上级行政代号')
    parent_id = fields.Many2one('dtdream.area', string='上级行政id')
    province = fields.Char(string="省级")
    country = fields.Char(string="市级",required=True)
    area_code = fields.Char(string="区号")
    area_leave = fields.Integer(string="行政等级",required=True)
    area_type = fields.Char(string="区域类别",required=True)

    def search_read(self, cr, uid, domain=None, fields=None, offset=0, limit=None, order=None, context=None):
        if 'child_ids' not in fields:
            domain = [ex for ex in domain if ex != ['parent_id', '=', False]]
        return super(dtdream_area, self).search_read(cr, uid, domain=domain)

# 继承丢单模型，将丢单原因设为必填
class dtdream_crm_lead_lost(models.Model):
    _inherit = "crm.lead.lost"

    lost_reason_id = fields.Many2one('crm.lost.reason', string='丢单原因', required=True)

class raise_warning(models.Model):
    _name = "raise.warning"

    @api.model
    def raise_warning(self,msg):
        raise ValidationError(msg)