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

    @api.constrains("family", "nation")
    def _check_family_null(self):
        for emergency in self.family:
            if emergency.emergency or not self.login_info_employee:
                return
        raise ValidationError(u"请至少设置一名紧急联系人")

    def _compute_basic_page(self):
        hr_user = self.env.ref("base.group_hr_user") in self.env.user.groups_id
        hr_manager = self.env.ref("base.group_hr_manager") in self.env.user.groups_id
        has_view = self.env.ref("dtdream_hr_resume.group_hr_resume_view") in self.env.user.groups_id
        has_edit = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id
        if self.env.user == self.user_id or has_view or has_edit or hr_manager or hr_user:
            self.can_view_info_basic = True
        else:
            self.can_view_info_basic = False

    def _compute_self_page(self):
        has_view = self.env.ref("dtdream_hr_resume.group_hr_resume_view") in self.env.user.groups_id
        has_edit = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id
        if self.env.user == self.user_id or has_view or has_edit:
            self.can_view_info_self = True
        else:
            self.can_view_info_self = False

    def _compute_can_edit_public(self):
        hr_user = self.env.ref("base.group_hr_user") in self.env.user.groups_id
        hr_manager = self.env.ref("base.group_hr_manager") in self.env.user.groups_id
        if hr_user or hr_manager:
            self.edit_public_info = True
        else:
            self.edit_public_info = False

    def _compute_can_edit_basic(self):
        hr_user = self.env.ref("base.group_hr_user") in self.env.user.groups_id
        hr_manager = self.env.ref("base.group_hr_manager") in self.env.user.groups_id
        has_edit = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id
        if has_edit or hr_user or hr_manager:
            self.edit_basic_info = True
        else:
            self.edit_basic_info = False

    def _compute_can_edit_self(self):
        has_edit = self.env.ref("dtdream_hr_resume.group_hr_resume_edit") in self.env.user.groups_id
        if has_edit or self.env.user == self.user_id:
            self.edit_self_info = True
        else:
            self.edit_self_info = False

    def _compute_login_equal_employee(self):
        if self.user_id == self.env.user:
            self.login_info_employee = True
        else:
            self.login_info_employee = False

    def track_family_change(self, family):
        message = u'''<ul class='o_mail_thread_message_tracking'><li>家庭成员:<table border='1px'><thead><tr>
                    <th style='width: 40px;'>动作</th><th style='width: 50px;'>关系</th><th style='width: 80px'>姓名</th>
                    <th style='width: 160px'> 工作单位</th><th style='width: 160px'>地址</th><th style='width: 60px;'>邮编</th>
                    <th style='width: 100px'>邮箱</th><th style='width: 80px'>联系电话</th>
                    <th style='width: 100px'>紧急联系人</th></tr></thead><tbody>'''
        add = u''
        family = sorted(family, key=lambda family: family[1])
        tracked = False
        for rec in family:
            if not rec[1] and rec[0] != 0:
                continue
            cr = self.env['hr.employee.family'].search([('id', '=', rec[1])])
            if rec[0] == 1:
                tracked = True
                field = rec[2]
                if field.get('relation', None):
                    message += u"<tr><td>修改</td><td style='color: red;'>%s</td>" % field.get('relation')
                else:
                    message += u"<tr><td>修改</td><td>%s</td>" % cr.relation
                if field.get('name', None):
                    message += u"<td style='color: red;'>%s</td>" % field.get('name')
                else:
                    message += u"<td>%s</td>" % cr.name
                if field.get('company', None):
                    message += u"<td style='color: red;'>%s</td>" % field.get('company')
                else:
                    message += u"<td>%s</td>" % cr.company
                if field.get('address', None):
                    message += u"<td style='color: red;'>%s</td>" % field.get('address')
                else:
                    message += u"<td>%s</td>" % cr.address
                if field.get('postcode', None):
                    message += u"<td style='color: red;'>%s</td>" % field.get('postcode')
                else:
                    message += u"<td>%s</td>" % cr.postcode
                if field.get('mail', None):
                    message += u"<td style='color: red;'>%s</td>" % field.get('mail')
                else:
                    message += u"<td>%s</td>" % cr.mail
                if field.get('tel', None):
                    message += u"<td style='color: red;'>%s</td>" % field.get('tel')
                else:
                    message += u"<td>%s</td>" % cr.tel
                if str(field.get('emergency', '')):
                    message += u"<td style='color: red;'>%s</td></tr>" % field.get('emergency')
                else:
                    message += u"<td>%s</td></tr>" % cr.emergency
            elif rec[0] == 0:
                tracked = True
                field = rec[2]
                add += u'''<tr style='color: red;'><td>新增</td><td>{0}</td><td>{1}</td><td>{2}</td>
                         <td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td></tr>'''.format(
                    field.get('relation'), field.get('name'), field.get('company'), field.get('address'),
                    field.get('postcode'), field.get('mail'), field.get('tel'), field.get('emergency'))
            elif rec[0] == 2:
                tracked = True
                message += u'''<tr style='color: red;'><td>删除</td><td>{0}</td><td>{1}</td><td>{2}</td>
                         <td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td></tr>'''.format(cr.relation,
                        cr.name, cr.company, cr.address, cr.postcode, cr.mail, cr.tel, cr.emergency)
        if not tracked:
            return ''
        message += add + u"</tbody></table></li></ul>"
        return message

    @api.multi
    def write(self, vals):
        message = self.track_family_change(vals.get('family', ''))
        if message:
            self.message_post(body=message)
        return super(dtdream_hr_infor, self).write(vals)

    account = fields.Char(string="帐号")
    byname = fields.Char(string="等价花名", track_visibility='onchange')
    recruit = fields.Selection([('0', "社会招聘"), ('1', "校园招聘")], string="招聘类型")
    work_place = fields.Char(string="常驻工作地")
    recruit_place = fields.Char(string="招聘所在地")
    expatriate = fields.Boolean(string="是否外派")
    travel_grant = fields.Boolean(string='是否享有交通补助')
    standard_mobile_fee = fields.Integer(string='手机话费标准')
    nation = fields.Char(string="民族", track_visibility='onchange')
    political = fields.Selection([("0", "党员"), ("1", "群众"), ("2", "其它")], string="政治面貌", track_visibility='onchange')
    postcode = fields.Char(string="邮编", track_visibility='onchange')
    birthday = fields.Date(string="出生日期", track_visibility='onchange')
    Birthplace_province = fields.Many2one("dtdream.hr.province", string="籍贯(省)", track_visibility='onchange')
    Birthplace_state = fields.Many2one("dtdream.hr.state", string="籍贯(市)", track_visibility='onchange')
    graduate = fields.Boolean(string="是否应届生", track_visibility='onchange')
    family = fields.One2many("hr.employee.family", "employee", string="家庭成员")
    province_hukou = fields.Many2one("dtdream.hr.province", string="户口所在地(省)", track_visibility='onchange')
    state_hukou = fields.Many2one("dtdream.hr.state", string="户口所在地(市)", track_visibility='onchange')
    nature_hukou = fields.Selection([("0", "城镇"), ("1", "农村")], string="户口性质", track_visibility='onchange')
    endtime_shebao = fields.Date(string="上家单位社保缴纳截止月份", track_visibility='onchange')
    endtime_gongjijin = fields.Date(string="上家单位公积金缴纳截止月份", track_visibility='onchange')
    ahead_prov = fields.Many2one("dtdream.hr.province", string="原社保缴纳地(省)", track_visibility='onchange')
    ahead_state = fields.Many2one("dtdream.hr.state", string="原社保缴纳地(市)", track_visibility='onchange')
    now_prov = fields.Many2one("dtdream.hr.province", string="申请社保缴纳地(省)", track_visibility='onchange')
    now_state = fields.Many2one("dtdream.hr.state", string="申请社保缴纳地(市)", track_visibility='onchange')
    shebao_prov = fields.Many2one("dtdream.hr.province", string="原公积金缴纳地(省)", track_visibility='onchange')
    gongjijin_state = fields.Many2one("dtdream.hr.state", string="原公积金缴纳地(市)", track_visibility='onchange')
    oil_card = fields.Char(string="油卡编号", track_visibility='onchange')
    has_oil = fields.Boolean(string="已办理中大一卡通", track_visibility='onchange')
    bankaddr = fields.Char(string="开户行地址")
    bankcardno = fields.Char(string="银行卡号")
    login_info_employee = fields.Boolean(string="员工是否当前登入人", compute=_compute_login_equal_employee)
    can_view_info_self = fields.Boolean(string="员工自助信息是否可见", compute=_compute_self_page)
    can_view_info_basic = fields.Boolean(string="员工基本信息是否可见", compute=_compute_basic_page, default=True)
    edit_public_info = fields.Boolean(string="是否有权限编辑公开信息", compute=_compute_can_edit_public, default=True)
    edit_basic_info = fields.Boolean(string="是否有编辑基本信息权限", compute=_compute_can_edit_basic, default=True)
    edit_self_info = fields.Boolean(string="是否有权限编辑自助信息", compute=_compute_can_edit_self)
    active = fields.Boolean(default=True, string='有效')


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


class dtdream_hr_department(models.Model):
    _inherit = 'hr.department'

    @api.multi
    def message_subscribe_users(self, user_ids=None, subtype_ids=None):
        """ Wrapper on message_subscribe, using users. If user_ids is not
            provided, subscribe uid instead. """
        user_ids = []
        result = self.message_subscribe(self.env['res.users'].browse(user_ids).mapped('partner_id').ids, subtype_ids=subtype_ids)
        return result
