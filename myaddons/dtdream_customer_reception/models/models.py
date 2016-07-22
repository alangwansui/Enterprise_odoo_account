# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_customer_reception(models.Model):
    _name = 'dtdream.customer.reception'
    _description = u"客户接待"
    _inherit = ['mail.thread']

    write_time = fields.Char(string='填单时间')
    bill_num = fields.Char(string='单据号')
    duty_tel = fields.Char(string='客工部值班电话')
    name = fields.Many2one('hr.employee', string='员工姓名')
    workid = fields.Char('工号')
    iphone = fields.Char(string='联系电话')
    post = fields.Char(string='职务')
    home = fields.Char(string='常驻地')
    department = fields.Many2one('hr.department', string='所属部门')
    code = fields.Char(string='部门编码')
    customer = fields.Many2one('res.partner', string='客户名称')
    project = fields.Many2one('crm.lead', string='项目名称')
    visit_count = fields.Integer(string='来访人数')
    guest = fields.One2many('dtdream.guest.honour', 'customer_reception')
    visit_date = fields.Date(string='来访日期')
    inter_tel = fields.Char(string='接口人联系方式')
    background = fields.Text(string='客户背景')
    purpose = fields.Many2one('dtdream.visit.purpose', string='来访目的')
    accompany_leads = fields.Many2many('hr.employee', string='公司出席陪同领导')
    interpreter = fields.Many2many('hr.employee', string='汇报讲解人员')
    participants = fields.Many2many('hr.employee', string='公司参会人员名单')
    room_capacity = fields.Integer(string='会议室可容纳人数')
    busy_time_room = fields.Datetime(string='会议室使用时间')
    car = fields.Boolean(string='小车')
    car_num = fields.Integer()
    commercial_vehicle = fields.Boolean(string='商务车')
    commercial_vehicle_num = fields.Boolean()
    bicycle = fields.Boolean(string='自行车')
    path = fields.One2many('dtdream.visit.path', 'customer_reception')
    driver = fields.Boolean(string='司机')
    assistance = fields.Boolean(string='接机/接站人员')
    card = fields.Boolean(string='接机牌')
    flower = fields.Boolean(string='鲜花')





    state = fields.Selection([('0', '草稿'),
                              ('1', '部门审批'),
                              ('2', '客工部审批'),
                              ('3', '接待安排与执行'),
                              ('4', '执行评价'),
                              ('99', '完成'),
                              ], string='状态', default='0')


class dtdream_guest_honour(models.Model):
    _name = 'dtdream.guest.honour'

    name_guest = fields.Char(string='姓名')
    post_guest = fields.Char(string='职务')
    customer_reception = fields.Many2one('dtdream.customer.reception')


class dtdream_visit_purpose(models.Model):
    _name = 'dtdream.visit.purpose'

    visit_type = fields.Char(string='来访目的')


class dtdream_visit_path(models.Model):
    _name = 'dtdream.visit.path'

    start_time = fields.Datetime(string='出发时间')
    starting = fields.Char(string='出发地点')
    end_time = fields.Datetime(string='到达时间')
    destination = fields.Char(string='到达地点')
    customer_reception = fields.Many2one('dtdream.customer.reception')





