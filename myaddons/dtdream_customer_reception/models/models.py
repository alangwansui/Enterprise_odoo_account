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
    customer_v = fields.Selection([('0', '是'), ('1', '否')], string='是否价值客户')
    project = fields.Many2one('crm.lead', string='项目名称')
    visit_count = fields.Char(string='来访人数')
    guest = fields.One2many('dtdream.guest.honour', 'customer_reception')
    visit_date = fields.Date(string='来访日期')
    inter_tel = fields.Char(string='接口人联系方式')
    background = fields.Text(string='客户背景')
    purpose = fields.Many2one('dtdream.visit.purpose', string='来访目的')
    accompany_leads = fields.Many2many('hr.employee', string='公司出席陪同领导')
    interpreter = fields.Many2many('hr.employee', string='汇报讲解人员')
    participants = fields.Many2many('hr.employee', string='公司参会人员名单')
    room_capacity = fields.Char(string='会议室可容纳人数')
    busy_time_room = fields.Datetime(string='会议室使用时间')
    ppt = fields.Boolean(string='PPT')
    meeting = fields.Many2one('dtdream.meeting.room', string='会议室预订')
    reserve_time = fields.Datetime(string='会议室预订时间')
    car = fields.Boolean(string='小车')
    car_num = fields.Char(size=3, )
    commercial_vehicle = fields.Boolean(string='商务车')
    commercial_vehicle_num = fields.Char()
    bicycle = fields.Boolean(string='自行乘车')
    path = fields.One2many('dtdream.visit.path', 'customer_reception')
    driver = fields.Boolean(string='司机')
    assistance = fields.Boolean(string='接机/接站人员')
    card = fields.Boolean(string='接机牌')
    flower = fields.Boolean(string='鲜花')
    single_room = fields.Boolean(string='标准单人房')
    single_room_num = fields.Char()
    double_room = fields.Boolean(string='标准双人房')
    double_room_num = fields.Char()
    room_self = fields.Boolean(string='自理安排酒店')
    hotel = fields.Selection([('5', '五星级'), ('4', '四星级'), ('3', '三星级或快捷酒店'), ('0', '其它')])
    hotel_position = fields.Selection([('0', '商业区'), ('1', '景区')])
    payment_hotel = fields.Selection([('0', '申请人垫付'), ('1', '客户自理')])
    dinner = fields.Selection([('100', '人均100以下'), ('300', '人均101-300'), ('500', '人均301-500'),
                               ('501', '人均500以上')])
    dinner_position = fields.Selection([('0', '商业区'), ('1', '景区')])
    payment_dinner = fields.Selection([('0', '申请人垫付'), ('1', '客户自理')])
    memories = fields.Many2one('dtdream.customer.memories', string='纪念品')
    memories_num = fields.Char()
    hotel_fee = fields.Char(string='住宿费')
    dinner_fee = fields.Char(string='就餐费')
    car_fee = fields.Char(string='车辆费')
    advertise_fee = fields.Char(string='公司宣传费')
    other_fee = fields.Char(string='其它费用')
    total_fee = fields.Char(string='总计')
    receptionist = fields.Many2one('hr.employee', string='指定客户接待执行人')
    summary = fields.Text(string='接待小结')
    score = fields.Selection([('1', '1'), ('5', '5'), ('10', '10')])
    state = fields.Selection([('0', '草稿'),
                              ('1', '部门审批'),
                              ('2', '客工部审批'),
                              ('3', '接待安排与执行'),
                              ('4', '执行评价'),
                              ('99', '完成'),
                              ], string='状态', default='0')


class dtdream_guest_honour(models.Model):
    _name = 'dtdream.guest.honour'

    name_guest = fields.Char(string='主宾姓名')
    post_guest = fields.Char(string='职务')
    customer_reception = fields.Many2one('dtdream.customer.reception')


class dtdream_visit_purpose(models.Model):
    _name = 'dtdream.visit.purpose'

    visit_type = fields.Char(string='来访目的')


class dtdream_meeting_room(models.Model):
    _name = 'dtdream.meeting.room'

    name = fields.Char(string='会议室名称')


class dtdream_visit_path(models.Model):
    _name = 'dtdream.visit.path'

    start_time = fields.Datetime(string='出发时间')
    starting = fields.Char(string='出发地点')
    end_time = fields.Datetime(string='到达时间')
    destination = fields.Char(string='到达地点')
    customer_reception = fields.Many2one('dtdream.customer.reception')


class dtdream_customer_memories(models.Model):
    _name = 'dtdream.customer.memories'

    name = fields.Char(string='纪念品名称')





