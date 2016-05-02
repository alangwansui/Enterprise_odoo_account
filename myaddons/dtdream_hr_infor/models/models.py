# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_hr_infor(models.Model):
    _inherit = "hr.employee"

    @api.onchange("province_hukou", "ahead_prov", "now_prov", "shebao_prov")
    def _state_hukou_domain(self):
        return {"domain": {
            "state_hukou": ['|', ('pro_name', '=', self.province_hukou.name), ('province', "=", self.province_hukou.id)],
            "ahead_state": ['|', ('pro_name', '=', self.ahead_prov.name), ('province', "=", self.ahead_prov.id)],
            "now_state": ['|', ('pro_name', '=', self.now_prov.name), ('province', "=", self.now_prov.id)],
            "gongjijin_state": ['|', ('pro_name', '=', self.shebao_prov.name), ('province', "=", self.shebao_prov.id)]}}

    account = fields.Char(string="账号", required=True)
    byname = fields.Char(string="等价花名")
    recruit = fields.Selection([('0', "社会招聘"), ('1', "校园招聘")], string="招聘类型", required=True)
    work_place = fields.Char(string="常驻工作地", required=True)
    recruit_place = fields.Char(string="招聘所在地", required=True)
    expatriate = fields.Boolean(string="是否外派")
    nation = fields.Char(string="民族", required=True)
    political = fields.Selection([("0", "党员"), ("1", "群众"), ("2", "其它")], string="政治面貌", required=True)
    marry = fields.Selection([("0", "未婚"), ("1", "已婚"), ("2", "离异")], string="婚姻", required=True)
    child = fields.Integer(string="子女数")
    icard = fields.Char(string="身份证", required=True)
    postcode = fields.Char(string="邮编", required=True)
    birthday = fields.Date(string="出生日期", required=True)
    Birthplace = fields.Char(string="籍贯", required=True)
    graduate = fields.Boolean(string="是否应届生")
    family = fields.One2many("hr.employee.family", "employee", string="家庭成员")
    province_hukou = fields.Many2one("dtdream.hr.province", string="户口所在地(省)", required=True)
    state_hukou = fields.Many2one("dtdream.hr.state", string="户口所在地(市)", required=True)
    nature_hukou = fields.Selection([("0", "城镇"), ("1", "农村")], string="户口性质", required=True)
    endtime_shebao = fields.Date(string="上家单位社保缴纳截止月份", required=True)
    endtime_gongjijin = fields.Date(string="上家单位公积金缴纳截止月份", required=True)
    ahead_prov = fields.Many2one("dtdream.hr.province", string="原社保缴纳地(省)", required=True)
    ahead_state = fields.Many2one("dtdream.hr.state", string="原社保缴纳地(市)", required=True)
    now_prov = fields.Many2one("dtdream.hr.province", string="申请社保缴纳地(省)",  required=True)
    now_state = fields.Many2one("dtdream.hr.state", string="申请社保缴纳地(市)", required=True)
    shebao_prov = fields.Many2one("dtdream.hr.province", string="原公积金缴纳地(省)", required=True)
    gongjijin_state = fields.Many2one("dtdream.hr.state", string="原公积金缴纳地(市)", required=True)
    oil_card = fields.Char(string="油卡编号")
    has_oil = fields.Boolean(string="已办理中大一卡通")
    contract = fields.One2many("dtdream.hr.contract", "name", string="合同")


class dtdream_hr_family(models.Model):
    _name = "hr.employee.family"

    employee = fields.Many2one("hr.employee", string="员工")
    relation = fields.Char(string="关系")
    name = fields.Char(string="姓名")
    company = fields.Char(string="工作单位")
    address = fields.Char(string="地址")
    postcode = fields.Char(string="邮编")
    mail = fields.Char(string="邮箱")
    tel = fields.Char(string="联系电话")
    emergency = fields.Boolean(string="紧急联系人")


class dtdream_hr_province(models.Model):
    _name = "dtdream.hr.province"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("name", operator, name), ("abbre", operator, name)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get()

    name = fields.Char(string="省份", required=True)
    code = fields.Char(string="简称")
    abbre = fields.Char(string="缩写", required=True)
    state = fields.One2many("dtdream.hr.state", "province", string="市区")

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", u'省份必须是唯一的'),
    ]


class dtdream_hr_state(models.Model):
    _name = "dtdream.hr.state"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("name", operator, name), ("abbre", operator, name)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get()

    name = fields.Char(string="市区", required=True)
    abbre = fields.Char(string="缩写", required=True)
    pro_name = fields.Char(string="省份")
    province = fields.Many2one("dtdream.hr.province", string="省份")


class dtdream_hr_contract(models.Model):
    _name = "dtdream.hr.contract"

    @api.depends('name')
    def _compute_num_department(self):
        for rec in self:
            rec.num = rec.name.job_number
            rec.department = rec.name.department_id.complete_name

    name = fields.Many2one("hr.employee", string="花名", required=True)
    num = fields.Char(string="工号", compute=_compute_num_department)
    department = fields.Char(string="部门", compute=_compute_num_department)
    date_start = fields.Date(string="合同开始日期", required=True)
    date_stop = fields.Date(string="合同结束日期", required=True)

    _sql_constraints = [
        ("date_check", "CHECK(date_start < date_stop)", u'合同结束日期必须大于合同开始日期')
    ]




