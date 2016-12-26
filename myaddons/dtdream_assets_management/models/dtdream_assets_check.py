# -*- coding: utf-8 -*-

from openerp import models, fields, api
from lxml import etree
from openerp.osv import expression
from openerp.exceptions import AccessError
from datetime import datetime


class dtdream_assets_check(models.Model):
    _name = 'dtdream.assets.check'
    _description = u'资产盘点'
    _rec_name = 'check_code'
    _order = 'state asc, create_date desc'
    _inherit = ['mail.thread']

    def compute_check_date(self):
        if self.state == "1":
            self.selfcheck_date = False
        else:
            self.selfcheck_date = self.write_date

    @api.depends('name')
    def compute_workid_department(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id
            rec.department_code = rec.name.department_id.code

    @api.depends('asset_type')
    def compute_account_discount(self):
        for rec in self:
            rec.account = rec.asset_type.account
            rec.discount = rec.asset_type.discount

    @api.depends('price', 'disprice', 'discount_month', 'discount')
    def compute_disprice_total(self):
        for rec in self:
            if rec.discount != 0:
                rec.disprice_total = ((rec.price - rec.disprice) / rec.discount) * rec.discount_month

    @api.depends('enable_date')
    def compute_discount_month(self):
        for rec in self:
            if rec.enable_date:
                rec.discount_month = datetime.now().month - datetime.strptime(rec.enable_date, '%Y-%m-%d').month

    @api.depends("price", "disprice_total")
    def compute_net_price(self):
        for rec in self:
            rec.net_price = rec.price - rec.disprice_total

    def compute_assets_amongst(self):
        for rec in self:
            if rec.env.user == rec.name.user_id:
                rec.amongst = True
            else:
                rec.amongst = False

    def compute_assets_manage(self):
        for rec in self:
            if rec.env.ref("dtdream_assets_management.dtdream_assets_manage") in rec.env.user.groups_id:
                rec.is_manage = True
            else:
                rec.is_manage = False

    def compute_assets_officer(self):
        for rec in self:
            if rec.env.ref("dtdream_assets_management.dtdream_assets_officer") in rec.env.user.groups_id:
                rec.is_officer = True
            else:
                rec.is_officer = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(dtdream_assets_check, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if res['type'] == "form":
            doc.xpath("//form")[0].set("edit", "false")
            doc.xpath("//form")[0].set("create", "false")
        if res['type'] == "tree":
            doc.xpath("//tree")[0].set("edit", "false")
            doc.xpath("//tree")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        uid = self._context.get('uid', '')
        manage = self.env.ref("dtdream_assets_management.dtdream_assets_manage") in self.env.user.groups_id
        officer = self.env.ref("dtdream_assets_management.dtdream_assets_officer") in self.env.user.groups_id
        if manage:
            domain = domain if domain else []
        elif officer:
            domain = expression.AND([['|', ('name.user_id', '=', uid),
                                      ('name.department_id', '=', self.env.user.employee_ids.department_id.id)], domain])
        else:
            domain = expression.AND([[('name.user_id', '=', uid)], domain])
        return super(dtdream_assets_check, self).search_read(domain=domain, fields=fields, offset=offset,
                                                             limit=limit, order=order)

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_assets_check_menu(self):
        menu = self.env['ir.ui.menu'].search([('name', '=', u'盘点')], limit=1)
        action = menu.action.id
        return menu.parent_id.id, action

    @api.model
    def create(self, vals):
        vals['check_code'] = self.env['ir.sequence'].next_by_code('dtdream.assets.check')
        return super(dtdream_assets_check, self).create(vals)

    def check_access_assets_check(self):
        for rec in self:
            user = self.env.user
            if self.env.ref("dtdream_assets_management.dtdream_assets_manage") in self.env.user.groups_id:
                return True
            elif self.env.ref("dtdream_assets_management.dtdream_assets_officer") in self.env.user.groups_id:
                if rec.name.user_id != user and rec.name.department_id != user.employee_ids.department_id:
                    return False
            elif rec.name.user_id != user:
                return False
            return True

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(dtdream_assets_check, self).read(fields=fields, load=load)
        perm_read = self.check_access_assets_check()
        if load == '_classic_read' and not perm_read:
            raise AccessError('由于安全限制，请求的操作不能被完成。请联系你的系统管理员。' +
                              '\n\n(单据类型: dtdream.assets.check, 操作: read.)')
        return result

    check_code = fields.Char(string='盘点编号')
    name = fields.Many2one('hr.employee', string='资产责任人')
    workid = fields.Char(string='工号', compute=compute_workid_department)
    department = fields.Many2one('hr.department', string='归属部门', compute=compute_workid_department)
    department_code = fields.Char(string='归属部门编码', compute=compute_workid_department)
    bill_num = fields.Char(string='资产订单号', size=32)
    asset_code = fields.Char(string='资产编码', size=32)
    asset_serial = fields.Char(string='资产串号(SN)', size=32)
    enable_date = fields.Date(string='启用日期')
    in_use = fields.Date(string='领用日期')
    asset_name = fields.Many2one('dtdream.assets.name', string='资产名称')
    asset_type = fields.Many2one('dtdream.assets.type', string='资产类别')
    asset_desc = fields.Char(string='资产配置', size=128)
    asset_spec = fields.Char(string='资产规格', size=128)
    account = fields.Char(string='会计科目', compute=compute_account_discount)
    price = fields.Float(string='资产原值(元)')
    discount = fields.Integer(string='折旧年限(月)', compute=compute_account_discount)
    disprice = fields.Float(string='资产残值(元)')
    disprice_total = fields.Float(string='累计折旧额(元)', compute=compute_disprice_total)
    discount_month = fields.Integer(string='已计提折旧月份数(月)', compute=compute_discount_month)
    net_price = fields.Float(string='资产净值(元)', compute=compute_net_price)
    store_place = fields.Many2one('dtdream.assets.store.place', string='资产位置')
    quality_date = fields.Date(string='质保日期')
    quality_place_province = fields.Many2one('dtdream.hr.province', string='质保省份')
    quality_place_city = fields.Many2one('dtdream.hr.state', string='质保市区')
    explain = fields.Text(string='说明')
    supplier = fields.Many2one('res.partner', string='供应商')
    has_label = fields.Selection([('0', '否'), ('1', '是')], string='标签是否粘贴')
    useable = fields.Selection([('0', '否'), ('1', '是')], string='是否可使用', default='1')
    unused = fields.Selection([('0', '否'), ('1', '是')], string='是否闲置', default='0')
    selfcheck_date = fields.Date(string='自盘时间')
    mark = fields.Text(string='备注')
    state = fields.Selection([('0', '草稿'), ('1', '盘点中'), ('101', '异常'), ('99', '完成')], string='状态', default='0')
    amongst = fields.Boolean(string='是否资产责任人', compute=compute_assets_amongst)
    is_manage = fields.Boolean(string='是否资产管理员', compute=compute_assets_manage)
    is_officer = fields.Boolean(string='是否部门资产管理员', compute=compute_assets_officer)
    assets_manage = fields.Many2one('dtdream.assets.management')
    current_approve = fields.Many2one('hr.employee', string='当前处理人')

    @api.multi
    def wkf_check(self):
        self.write({"state": '1', "current_approve": self.name.id})

    @api.multi
    def wkf_except(self):
        self.write({"state": '101'})

    @api.multi
    def wkf_done(self):
        self.write({"state": '99', "current_approve": ''})
