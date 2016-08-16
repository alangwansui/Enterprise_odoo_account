# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api


class dtdream_budget_travel(models.Model):
    _name = 'dtdream.budget.travel'
    _description = u'公务差旅费'
    travel_travel = fields.Float(string='差旅费')
    travel_bus = fields.Float(string='市内交通费')
    travel_mobile = fields.Float(string='手机话费')

    @api.onchange('travel_travel','travel_bus','travel_mobile')
    def compute_travel_total(self):
        self.travel_total=self.travel_travel+self.travel_bus+self.travel_mobile
    travel_remark = fields.Char(string='备注')
    travel_budget_id = fields.Many2one('dtdream.budget',string='预算')


class dtdream_budget_daily(models.Model):
    _name = 'dtdream.budget.daily'
    _description = u'日常业务费'
    daily_name = fields.Char(string='项目或事务名称')
    daily_fee = fields.Float(string='员工预算金额')
    daily_remark = fields.Char(string='备注')
    daily_budget_id = fields.Many2one('dtdream.budget',string='预算')


class dtdream_budget_zhuanx(models.Model):
    _name = 'dtdream.budget.zhuanx'
    _description = u'专项业务费'
    zhuanx_name = fields.Char(string='专项名称')
    zhuanx_fee = fields.Float(string='员工预算金额')
    zhuanx_remark = fields.Char(string='备注')
    zhuanx_budget_id = fields.Many2one('dtdream.budget',string='预算')


class dtdream_budget_xingz(models.Model):
    _name = 'dtdream.budget.xingz'
    _description = u'行政平台费'
    xingz_name = fields.Char(string='名称')
    xingz_fee = fields.Float(string='员工预算金额')
    xingz_remark = fields.Char(string='备注')
    xingz_budget_id = fields.Many2one('dtdream.budget',string='预算')


class dtdream_budget(models.Model):
    _name = 'dtdream.budget'
    _description = u'预算管理'
    current_handler=fields.Many2one('hr.employee',string="当前处理人")
    his_handler=fields.Many2many('hr.employee',string="历史审批人")
    manager = fields.Many2one('hr.employee',string="直接主管")
    signer = fields.Many2one('hr.employee',string="权签人")
    is_sign = fields.Boolean(string="是否跳过权签")
    applicant = fields.Many2one('hr.employee',string="申请人",default=lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]))
    apply_time = fields.Datetime(string='申请时间',default=datetime.now())
    full_name = fields.Char(string="姓名",default = lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).full_name)
    job_number = fields.Char(string="工号",default = lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).job_number)
    department = fields.Many2one("hr.department",string="部门",default=lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.id)
    department_code = fields.Char(string="部门编码",default = lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.code)
    @api.one
    @api.depends("name")
    def _compute_fields(self):
        max_rec = ''
        id_prefix = 'YS'+datetime.strftime(datetime.today(),"%Y%m%d")
        self._cr.execute("select budget_id from dtdream_budget where budget_id like '"+id_prefix+"%' order by id desc limit 1")
        for rec in self._cr.fetchall():
            max_rec = rec[0]
        if max_rec:
            self.budget_id='YS'+str(int(max_rec[2:])+1)
        else:
            self.budget_id=id_prefix+'001'
    budget_id=fields.Char(string="单号",compute=_compute_fields,store=True)
    state=fields.Selection([("0","草稿"),("1","主管审批"),("2","权签人审批"),("3","已审批")],string="状态")
    name= fields.Selection([
        (datetime.strftime(datetime.today()+relativedelta(months=2),"%Y%m"),datetime.strftime(datetime.today()+relativedelta(months=2),"%Y%m")),
        (datetime.strftime(datetime.today()+relativedelta(months=1),"%Y%m"),datetime.strftime(datetime.today()+relativedelta(months=1),"%Y%m")),
        (datetime.strftime(datetime.today(),"%Y%m"),datetime.strftime(datetime.today(),"%Y%m")),
        (datetime.strftime(datetime.today()-relativedelta(months=1),"%Y%m"),datetime.strftime(datetime.today()-relativedelta(months=1),"%Y%m")),
        (datetime.strftime(datetime.today()-relativedelta(months=2),"%Y%m"),datetime.strftime(datetime.today()-relativedelta(months=2),"%Y%m")),
    ],string="预算月份",domain=[('asd','=','201608')])
    # name = fields.Many2one('dtdream.budget.month',string="预算月份")
    fee_types=fields.Many2many('dtdream.expense.catelog',string='费用类别')
    expensed_travel=fields.Float(string='已报销差旅费')
    expensed_daily=fields.Float(string='已报销日常业务费')
    expensed_zhuanx=fields.Float(string='已报销专项业务费')
    expensed_xingz=fields.Float(string='已报销行政平台费')

    def _default_fee_travel(self):
        return [(0, 0, {'travel_travel': 0.00, 'travel_bus': 0.00, 'travel_mobile': 0.00, 'travel_remark': ''})]
    def _default_fee_dzx(self,x,y,z):
        return [(0, 0, {x: '合计', y: 0.00, z: ''})]
    fee_travel = fields.One2many('dtdream.budget.travel','travel_budget_id',string='公务差旅费',default=_default_fee_travel)

    @api.depends('fee_travel')
    def _compute_fee_travel_total(self):
        self.fee_travel_total = 0
        for rec in self.fee_travel:
            self.fee_travel_total = rec.travel_travel+rec.travel_bus+rec.travel_mobile
    fee_travel_total = fields.Float(string='公务差旅费合计',compute=_compute_fee_travel_total,store=True)
    fee_daily = fields.One2many('dtdream.budget.daily','daily_budget_id',string='日常业务费')

    @api.depends('fee_daily')
    def _compute_fee_daily_total(self):
        self.fee_daily_total=0
        for rec in self.fee_daily:
            self.fee_daily_total += rec.daily_fee
    fee_daily_total=fields.Float(string='日常业务费合计',compute=_compute_fee_daily_total,store=True)
    fee_zhuanx = fields.One2many('dtdream.budget.zhuanx','zhuanx_budget_id',string='专项业务费')

    @api.depends('fee_zhuanx')
    def _compute_fee_zhuanx_total(self):
        self.fee_zhuanx_total=0
        for rec in self.fee_zhuanx:
            self.fee_zhuanx_total += rec.zhuanx_fee
    fee_zhuanx_total=fields.Float(string='专项业务费合计',compute=_compute_fee_zhuanx_total,store=True)
    fee_xingz = fields.One2many('dtdream.budget.xingz','xingz_budget_id',string='行政平台费')

    @api.depends('fee_xingz')
    def _compute_fee_xingz_total(self):
        self.fee_xingz_total=0
        for rec in self.fee_xingz:
            self.fee_xingz_total += rec.xingz_fee
    fee_xingz_total=fields.Float(string='行政平台费合计',compute=_compute_fee_xingz_total,store=True)

    @api.one
    @api.depends('fee_travel','fee_daily','fee_zhuanx','fee_xingz')
    def compute_all_total(self):
        self.all_total = self.fee_travel_total+self.fee_daily_total+self.fee_zhuanx_total+self.fee_xingz_total
    all_total = fields.Float(string='总金额',compute = compute_all_total)

    @api.multi
    def wkf_draft(self):
        # 草稿状态
        self.state='0'
        self.current_handler = ''

        # 自己是主管
        if self.applicant.department_id.manager_id.id == self.applicant.id:
            # 如果有上级部门
            if self.applicant.department_id.parent_id:
                self.manager = self.applicant.department_id.parent_id.manager_id
            # 如果没有上级部门
            else:
                self.manager = ''
        else:
            self.manager = self.applicant.department_id.manager_id

        #  申请人是第一审批人
        if self.applicant.id == self.applicant.department_id.no_one_auditor.id:
            # 主管是第二审批人
            if self.manager.id == self.applicant.department_id.no_two_auditor.id:
                self.is_sign = True
            else:
                self.signer = self.applicant.department_id.no_two_auditor
        else:
            #  主管是第一审批人
            if self.manager.id == self.applicant.department_id.no_one_auditor.id:
                if self.applicant.id == self.applicant.department_id.no_two_auditor.id:
                    self.is_sign = True
                else:
                    self.signer = self.applicant.department_id.no_two_auditor
            else:
                self.signer = self.applicant.department_id.no_one_auditor

    @api.multi
    def wkf_manager_review(self):
        # 主管审批
        self.state = '1'
        self.current_handler = self.manager


    @api.multi
    def wkf_signer_review(self):
        # 权签人审批
        self.state='2'
        self.current_handler = self.signer

    @api.multi
    def wkf_reviewed(self):
        # 已审批
        self.state='3'
        self.current_handler=''

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):


        print self._fields['name']._column_selection
        self._fields['name']._column_selection=[]
        self._fields['name']._column_selection=[('201608','201608')]
        print "-----------------",self._fields['name']._column_selection
        res = super(dtdream_budget, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        print res['fields']['name']['selection']
        # res['fields']['name']['selection']=[('201608','201608')]
        # self._fields['name'].selection = [('201600','201600')]
        print "wwwwwwww"

        return res


class dtdream_budget_wizard(models.TransientModel):
     _name = "dtdream.budget.wizard"
     reason = fields.Text("意见")
     temp=fields.Char(string="存储信息")

     @api.one
     def btn_confirm(self):
         current_record=self.env['dtdream.budget'].browse(self._context['active_id'])
         if current_record.state == '1':
             current_record.write({"his_handler": [(4,current_record.manager.id)]})
         if current_record.state == '2':
             current_record.write({"his_handler": [(4,current_record.signer.id)]})
         if self.temp=='reject':
             current_record.signal_workflow('btn_reject')
         elif self.temp=='agree':
             current_record.signal_workflow('btn_agree')


class dtdream_hr_employee_extend(models.Model):
    _inherit = "hr.employee"
    budget_ids = fields.One2many('dtdream.budget','applicant',string='预算')

class dtdream_budget_month(models.Model):
    _name="dtdream.budget.month"
    name=fields.Char(string='预算月份')





