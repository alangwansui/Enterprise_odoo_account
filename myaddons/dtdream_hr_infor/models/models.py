# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError


class dtdream_hr_infor(models.Model):
    _inherit = "hr.employee"

    @api.onchange("Birthplace_province")
    def _state_birthday_domain(self):
        self.Birthplace_state = False
        return {"domain": {"Birthplace_state": ['|', ('pro_name', '=', self.Birthplace_province.name),
                                                ('province', "=", self.Birthplace_province.id)]}}

    @api.onchange("province_hukou")
    def _state_hukou_domain(self):
        self.state_hukou = False
        return {"domain": {"state_hukou": ['|', ('pro_name', '=', self.province_hukou.name),
                                           ('province', "=", self.province_hukou.id)]}}

    @api.onchange("ahead_prov")
    def _state_ahead_domain(self):
        self.ahead_state = False
        return {"domain": {"ahead_state": ['|', ('pro_name', '=', self.ahead_prov.name),
                                           ('province', "=", self.ahead_prov.id)]}}

    @api.onchange("now_prov")
    def _state_now_domain(self):
        self.now_state = False
        return {"domain": {"now_state": ['|', ('pro_name', '=', self.now_prov.name),
                                         ('province', "=", self.now_prov.id)]}}

    @api.onchange("shebao_prov")
    def _state_shebao_domain(self):
        self.gongjijin_state = False
        return {"domain": {"gongjijin_state": ['|', ('pro_name', '=', self.shebao_prov.name),
                                               ('province', "=", self.shebao_prov.id)]}}

    @api.constrains("family")
    def _check_family_null(self):
        for emergency in self.family:
            if self.family.emergency:
                return
        raise ValidationError(u"请至少设置一名紧急联系人")

    def _compute_basic_self_page(self):
        has_view = self.env.ref("dtdream_hr_resume.group_hr_resume_view") in self.env.user.groups_id
        has_edit = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id
        if self.env.user == self.user_id or has_view or has_edit:
            self.can_view = True
        else:
            self.can_view = False

    def _compute_can_edit_public(self):
        hr_user = self.env.ref("base.group_hr_user") in self.env.user.groups_id
        hr_manager = self.env.ref("base.group_hr_manager") in self.env.user.groups_id
        if hr_user or hr_manager:
            self.edit_public = True
        else:
            self.edit_public = False

    def _compute_can_edit_basic(self):
        has_edit = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id
        if has_edit:
            self.edit_basic = True
        else:
            self.edit_basic = False

    def _compute_can_edit_self(self):
        has_edit = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id
        if has_edit or self.env.user == self.user_id:
            self.edit_self = True
        else:
            self.edit_self = False

    account = fields.Char(string="账号")
    byname = fields.Char(string="等价花名")
    recruit = fields.Selection([('0', "社会招聘"), ('1', "校园招聘")], string="招聘类型")
    work_place = fields.Char(string="常驻工作地")
    recruit_place = fields.Char(string="招聘所在地")
    expatriate = fields.Boolean(string="是否外派")
    nation = fields.Char(string="民族")
    political = fields.Selection([("0", "党员"), ("1", "群众"), ("2", "其它")], string="政治面貌")
    postcode = fields.Char(string="邮编")
    birthday = fields.Date(string="出生日期")
    Birthplace_province = fields.Many2one("dtdream.hr.province", string="籍贯")
    Birthplace_state = fields.Many2one("dtdream.hr.state")
    graduate = fields.Boolean(string="是否应届生", default=lambda self: True)
    family = fields.One2many("hr.employee.family", "employee", string="家庭成员")
    province_hukou = fields.Many2one("dtdream.hr.province", string="户口所在地(省)")
    state_hukou = fields.Many2one("dtdream.hr.state", string="户口所在地(市)")
    nature_hukou = fields.Selection([("0", "城镇"), ("1", "农村")], string="户口性质")
    endtime_shebao = fields.Date(string="上家单位社保缴纳截止月份")
    endtime_gongjijin = fields.Date(string="上家单位公积金缴纳截止月份")
    ahead_prov = fields.Many2one("dtdream.hr.province", string="原社保缴纳地(省)")
    ahead_state = fields.Many2one("dtdream.hr.state", string="原社保缴纳地(市)")
    now_prov = fields.Many2one("dtdream.hr.province", string="申请社保缴纳地(省)")
    now_state = fields.Many2one("dtdream.hr.state", string="申请社保缴纳地(市)")
    shebao_prov = fields.Many2one("dtdream.hr.province", string="原公积金缴纳地(省)")
    gongjijin_state = fields.Many2one("dtdream.hr.state", string="原公积金缴纳地(市)")
    oil_card = fields.Char(string="油卡编号")
    has_oil = fields.Boolean(string="已办理中大一卡通")
    can_view = fields.Boolean(string="员工自助和基本信息是否可见", compute=_compute_basic_self_page)
    edit_public = fields.Boolean(string="是否有权限编辑公开信息", compute=_compute_can_edit_public)
    edit_basic = fields.Boolean(string="是否有编辑基本信息权限", compute=_compute_can_edit_basic)
    edit_self = fields.Boolean(string="是否有权限编辑自助信息", compute=_compute_can_edit_self)


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





