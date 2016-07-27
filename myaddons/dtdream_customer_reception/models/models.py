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
    customer_v = fields.Selection([('0', '是'), ('1', '否')], string='是否价值客户', default='0')
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
    camera = fields.Boolean(string='摄影')
    water = fields.Boolean(string='瓶装水')
    tea = fields.Boolean(string='茶水')
    meeting_document = fields.Boolean(string='公司资料')
    seat_board = fields.Boolean(string='席位牌')
    banner = fields.Boolean(string='横幅')
    other_more = fields.Boolean(string='其它')
    other_more_text = fields.Text(string='其它准备')
    meeting = fields.Many2one('dtdream.meeting.room', string='会议室预订')
    reserve_time = fields.Datetime(string='会议室预订时间')
    car = fields.Boolean(string='小车')
    car_num = fields.Integer()
    commercial_vehicle = fields.Boolean(string='商务车')
    commercial_vehicle_num = fields.Integer()
    bicycle = fields.Boolean(string='自行乘车')
    path = fields.One2many('dtdream.visit.path', 'customer_reception')
    driver = fields.Boolean(string='司机')
    assistance = fields.Boolean(string='接机/接站人员')
    card = fields.Boolean(string='接机牌')
    flower = fields.Boolean(string='鲜花')
    single_room = fields.Boolean(string='标准单人房')
    single_room_num = fields.Integer()
    double_room = fields.Boolean(string='标准双人房')
    double_room_num = fields.Integer()
    room_self = fields.Boolean(string='自理安排酒店')
    hotel = fields.Selection([('5', '五星级'), ('4', '四星级'), ('3', '三星级或快捷酒店'), ('0', '其它')],
                             string='酒店标准', default='5')
    hotel_position = fields.Selection([('0', '商业区'), ('1', '景区')], string='酒店位置', default='0')
    payment_hotel = fields.Selection([('0', '申请人垫付'), ('1', '客户自理')], string='住宿结算方式', default='0')
    dinner = fields.Selection([('100', '人均100元以下'), ('300', '人均101-300元'), ('500', '人均301-500元'),
                               ('501', '人均500元以上')], string='用餐标准', default='100')
    dinner_position = fields.Selection([('0', '商业区'), ('1', '景区')], string='用餐地点', default='0')
    payment_dinner = fields.Selection([('0', '申请人垫付'), ('1', '客户自理')], string='用餐结算方式', default='0')
    memories = fields.Many2one('dtdream.customer.memories', string='纪念品')
    memories_num = fields.Integer()
    hotel_fee = fields.Char(string='住宿费(元)')
    dinner_fee = fields.Char(string='就餐费(元)')
    car_fee = fields.Char(string='车辆费(元)')
    advertise_fee = fields.Char(string='公司宣传费(元)')
    other_fee = fields.Char(string='其它费用(元)')
    total_fee = fields.Char(string='总计(元)')
    receptionist = fields.Many2one('hr.employee', string='指定客户接待执行人')
    summary = fields.Text(string='接待人员接待小结')
    score = fields.Selection([('1', '1分'), ('5', '5分'), ('10', '10分')])
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

    name = fields.Char(string='来访目的')
    config = fields.Many2one('dtdream.customer.reception.config')


class dtdream_meeting_room(models.Model):
    _name = 'dtdream.meeting.room'

    name = fields.Char(string='会议室名称')
    config = fields.Many2one('dtdream.customer.reception.config')


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
    config = fields.Many2one('dtdream.customer.reception.config')


class dtdream_customer_reception_config(models.Model):
    _name = 'dtdream.customer.reception.config'

    duty_phone = fields.Char(string='客工部值班电话')
    officer = fields.Many2one('hr.employee', string='客工部主管')
    car = fields.Many2one('hr.employee', string='车辆负责人')
    inter = fields.Many2one('hr.employee', string='企划部接口人')
    purpose = fields.One2many('dtdream.visit.purpose', 'config')
    memory = fields.One2many('dtdream.customer.memories', 'config')
    metting_room = fields.One2many('dtdream.meeting.room', 'config')


class dtdream_marketing_activities(models.Model):
    _name = 'dtdream.marketing.activities'

    activity = fields.Selection([('0', '技术交流'), ('1', '公司参观'), ('2', '高层拜访'), ('3', '现场会'),
                                 ('4', '第三方活动'), ('5', '样板点参观')], string='活动类型')
    activity_time = fields.Date(string='时间')
    activity_place = fields.Char(string='地点')
    customer = fields.Many2many(string='客户参与人员')
    company = fields.Many2many(string='公司参与人员')
    activity_content = fields.Text(string='活动内容')
    activity_result = fields.Text(string='结果')
    partner_customer = fields.Many2one('res.partner')


class dtdream_customer_res_partner(models.Model):
    _inherit = 'res.partner'

    marketing_activities = fields.One2many('dtdream.marketing.activities', 'partner_customer')
    customer_reception = fields.Integer()





