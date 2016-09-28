# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from lxml import etree
import time
from openerp.exceptions import ValidationError


class dtdream_grants_config(models.Model):
    _name = 'dtdream.grants.config'
    name = fields.Char(default='配置')
    total = fields.Integer(string='每月补助金发放金额(元)')

    @api.constrains('total')
    def _check_total_valid(self):
        if self.total<0:
            raise ValidationError("每月补助金发放金额不能为负数！")

    @api.multi
    def write(self, vals):
        if vals.has_key('total'):
            allocation_rec = self.env['dtdream.grants.allocation'].search([])
            for recc in allocation_rec:
                super(dtdream_grants_allocation, recc).unlink()
        return super(dtdream_grants_config,self).write(vals)

class dtdream_grants_allocation(models.Model):
    _name = 'dtdream.grants.allocation'
    name = fields.Char(default='补助金分配设置')
    you = fields.Integer(string='每月油卡充值金额(元)')
    fan = fields.Integer(string='每月中大卡充值金额(元)')

    @api.onchange('you','fan')
    def _compute_cash(self):
        total = self.env['dtdream.grants.config'].search([]).total
        self.cash = total-self.you-self.fan

    @api.constrains('you','fan')
    def check_total(self):
        total = self.env['dtdream.grants.config'].search([]).total
        self.cash = total-self.you-self.fan
        if self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).has_oil == False and self.fan != 0:
            raise ValidationError('未办理中大一卡通，无法充值，已办理中大一卡通的，请在自助信息里选择“已办理中大一卡通”!')
        if not self.env["hr.employee"].search([('user_id','=',self.env.user.id)]).oil_card and self.you !=0:
            raise ValidationError("无油卡信息，请先在自助信息添加油卡编号!")
        if self.you+self.fan > total:
            raise ValidationError('充值金额总和超出每月补助发放金额')
        if self.you < 0 or self.fan < 0:
            raise ValidationError('充值金额不能小于0')
    cash = fields.Integer(string='补助金转工资金额(元)',compute=_compute_cash,store=True)


class dtdream_grants(models.Model):
    _name = 'dtdream.grants'
    name = fields.Many2one("hr.employee",string='员工')

    @api.depends('name')
    def _compute_employee_info(self):
        for em in self:
            em.department = em.name.department_id.id
            em.you_id = em.name.oil_card
            if em.name.Inaugural_state == 'Inaugural_state_01':
                em.job_state = '在职'
            elif em.name.Inaugural_state == 'Inaugural_state_02':
                em.job_state = em.env['leaving.handle'].search([('name','=',em.name.id)]).actual_leavig_date
            em.full_name = em.name.full_name
            em.job_number = em.name.job_number
            if em.name.department_id.parent_id:
                em.top_department = em.name.department_id.parent_id.name
            else:
                em.top_department = em.name.department_id.name

    full_name = fields.Char(string="姓名",compute = _compute_employee_info,store=True)
    job_number = fields.Char(string="工号",compute = _compute_employee_info,store=True)
    top_department = fields.Char(string="一级部门",compute = _compute_employee_info,store=True)
    department = fields.Many2one('hr.department',string='部门',compute = _compute_employee_info,store=True)
    month = fields.Char(string='发放年月',default=(datetime.now()-relativedelta(months=1)+relativedelta(hours=8)).strftime('%Y%m'))
    you_id = fields.Char(string='油卡编号',compute = _compute_employee_info,store=True)
    you_fill = fields.Integer(string='油卡充值金额(元)')
    fan_fill = fields.Integer(string='中大卡充值金额(元)')

    @api.onchange('you_fill','fan_fill')
    def _compute_cash(self):
        total = self.env['dtdream.grants.config'].search([]).total
        self.cash = total-self.you_fill-self.fan_fill

    @api.constrains('you_fill','fan_fill','name')
    def check_total(self):
        total = self.env['dtdream.grants.config'].search([]).total
        self.cash = total-self.you_fill-self.fan_fill
        if self.name.has_oil == False and self.fan_fill != 0:
            raise ValidationError('未办理中大一卡通，无法充值，已办理中大一卡通的，请在自助信息里选择“已办理中大一卡通”!')
        if not self.name.oil_card and self.you_fill != 0:
            raise ValidationError("无油卡信息，请先在自助信息添加油卡编号!")
        if self.you_fill+self.fan_fill > total:
            raise ValidationError('充值金额总和超出每月补助发放金额')
        if self.you_fill < 0 or self.fan_fill < 0:
            raise ValidationError('充值金额不能小于0')

    cash = fields.Integer(string='转工资金额(元)',compute=_compute_cash,store=True)
    job_state = fields.Char(string='在职状态',compute = _compute_employee_info)
    if_created = fields.Boolean(string='是否是创建',default=True)

    @api.model
    def create(self, vals):
        res = super(dtdream_grants,self).create(vals)
        res.if_created = False
        return res


    def _compute_if_last_month(self):
        this_month = (datetime.today()+relativedelta(hours=8)).strftime('%Y%m')
        if int(self.month)-int(this_month) == -1:
            self.if_last_month = True
        else:
            self.if_last_month = False
    if_last_month = fields.Boolean(string='是否上月的充值记录',compute=_compute_if_last_month)

    @api.model
    def create_allocation_regularly(self):
        if (datetime.today()+relativedelta(hours=8)).strftime('%d')=='01':
            last_month = (datetime.now()-relativedelta(months=1)+relativedelta(hours=8)).strftime('%Y-%m')
            last_month_fir = last_month+'-01'
            this_month_fir = (datetime.now()+relativedelta(hours=8)).strftime('%Y-%m')+'-01'
            last_month_like = last_month+'%'
            # 上月1号入职之前在职员工
            zaizhi_employee = self.env['hr.employee'].search([('Inaugural_state','=','Inaugural_state_01'),('entry_day','<',last_month_fir)])
            for rec in zaizhi_employee:
                self.create({'name':rec.id,
                             'you_fill':self.env['dtdream.grants.allocation'].search([('create_uid','=',rec.user_id.id)]).you,
                             'fan_fill':self.env['dtdream.grants.allocation'].search([('create_uid','=',rec.user_id.id)]).fan,
                             'cash':self.env['dtdream.grants.allocation'].search([('create_uid','=',rec.user_id.id)]).cash or self.env['dtdream.grants.config'].search([]).total})

            last_month_lizhi = self.env['leaving.handle'].search(['|',('actual_leavig_date','like',last_month_like),('actual_leavig_date','=',this_month_fir)])
            for recd in last_month_lizhi:
                if self.env['hr.employee'].search([('id','=',recd.name.id)]).Inaugural_state == 'Inaugural_state_02'and self.env['hr.employee'].search([('id','=',recd.name.id)]).entry_day<last_month_fir:
                    self.create({'name':recd.name.id,
                                 'you_fill':self.env['dtdream.grants.allocation'].search([('create_uid','=',recd.name.user_id.id)]).you,
                                 'fan_fill':self.env['dtdream.grants.allocation'].search([('create_uid','=',recd.name.user_id.id)]).fan,
                                 'cash':self.env['dtdream.grants.allocation'].search([('create_uid','=',recd.name.user_id.id)]).cash or self.env['dtdream.grants.config'].search([]).total})

    @api.constrains('month')
    def check_if_last_month(self):
        last_month = (datetime.today()-relativedelta(months=1)+relativedelta(hours=8)).strftime('%Y%m')
        if self.month != last_month:
            raise ValidationError('只能创建上个月的充值记录！')

    _sql_constraints = [
          ('one_grants_monthly','unique(name,month)','每人每个月只能创建一次补助金充值记录！')
     ]


