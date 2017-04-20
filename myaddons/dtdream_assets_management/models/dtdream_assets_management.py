# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.osv import expression
from openerp.exceptions import AccessError
from lxml import etree
import json


class dtdream_assets_management(models.Model):
    _name = 'dtdream.assets.management'
    _description = u'资产管理'
    _rec_name = 'asset_code'
    _inherit = ['mail.thread']

    @api.depends('name')
    def compute_workid_department(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.write({"department": rec.name.department_id.id})
            rec.department = rec.name.department_id
            rec.department_code = rec.name.department_id.code

    def compute_check_record(self):
        self.check_record = len(self.env["dtdream.assets.check"].search([("assets_manage", "=", self.id)]))

    @api.depends('asset_type')
    def compute_account_discount(self):
        for rec in self:
            rec.account = rec.asset_type.account
            rec.discount = rec.asset_type.discount

    @api.depends('price', 'disprice', 'discount_month', 'discount')
    def compute_disprice_total(self):
        for rec in self:
            if rec.discount != 0:
                rec.disprice_total = ((rec.price - rec.disprice) / (rec.discount * 12)) * rec.discount_month

    @api.depends('enable_date')
    def compute_discount_month(self):
        for rec in self:
            if rec.enable_date:
                now = datetime.now()
                enable_date = datetime.strptime(rec.enable_date, '%Y-%m-%d')
                rec.discount_month = (now.year - enable_date.year)*12 + now.month - enable_date.month

    @api.depends("price", "disprice_total")
    def compute_net_price(self):
        for rec in self:
            rec.net_price = rec.price - rec.disprice_total

    @api.onchange("quality_place_province")
    def province_change_domain(self):
        self.quality_place_city = False
        return {"domain": {"quality_place_city": ['|', ('pro_name', '=', self.quality_place_province.name),
                                                  ('province', "=", self.quality_place_province.id)]}}

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
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        codes = [mac.assets_code.asset_code for mac in self.env["dtdream.assets.mac.manage"].search([])]
        args = args or []
        domain = [("asset_code", "not in", codes)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get()

    @api.multi
    def message_poss(self, state, action, approve=''):
        self.message_post(body=u"""<table border="1" style="border-collapse: collapse;">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">下一处理人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, approve))

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
        return super(dtdream_assets_management, self).search_read(domain=domain, fields=fields, offset=offset,
                                                             limit=limit, order=order)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(dtdream_assets_management, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        manage = self.env.ref("dtdream_assets_management.dtdream_assets_manage") in self.env.user.groups_id
        if manage:
            return res
        doc = etree.XML(res['arch'])
        if res['type'] == "form":
            doc.xpath("//form")[0].set("edit", "false")
        if res['type'] == "tree":
            doc.xpath("//tree")[0].set("edit", "false")
        if res['type'] == "kanban":
            doc.xpath("//kanban")[0].set("edit", "false")
        res['arch'] = etree.tostring(doc)
        return res

    def check_access_assets_manage(self):
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

    def refresh_department_changed(self, result=None, load='_classic_read'):
        if load == '_classic_read':
            for cr in result:
                employee = cr.get('name', None)
                if isinstance(employee, tuple) and cr.get('department', None):
                    crr = self.env['hr.employee'].search([('id', '=', employee[0])])
                    cr['department'] = (crr.department_id.id, crr.department_id.complete_name)
            return result

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(dtdream_assets_management, self).read(fields=fields, load=load)
        result = self.refresh_department_changed(result, load)
        perm_read = self.check_access_assets_manage()
        if load == '_classic_read' and not perm_read:
            raise AccessError('由于安全限制，请求的操作不能被完成。请联系你的系统管理员。' +
                              '\n\n(单据类型: dtdream.assets.management, 操作: read.)')
        return result

    name = fields.Many2one('hr.employee', string='资产责任人')
    workid = fields.Char(string='工号', compute=compute_workid_department)
    department = fields.Many2one('hr.department', string='归属部门')
    department_code = fields.Char(string='归属部门编码', compute=compute_workid_department)
    bill_num = fields.Char(string='资产订单号', size=32)
    asset_code = fields.Char(string='资产编码', size=32)
    asset_serial = fields.Char(string='资产串号(SN)', size=32)
    enable_date = fields.Date(string='启用日期')
    in_use = fields.Date(string='领用日期')
    asset_name = fields.Many2one('dtdream.assets.name', string='资产名称')
    asset_type = fields.Many2one('dtdream.assets.type', string='资产类别')
    asset_desc = fields.Char(string='资产配置', size=256)
    asset_spec = fields.Char(string='资产规格', size=128)
    account = fields.Char(string='会计科目', compute=compute_account_discount)
    price = fields.Float(string='资产原值(元)')
    discount = fields.Integer(string='折旧年限(年)', compute=compute_account_discount)
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
    check_record = fields.Integer(string='盘点记录', compute=compute_check_record)
    is_manage = fields.Boolean(string='是否资产管理员', compute=compute_assets_manage, default=True)
    is_officer = fields.Boolean(string='是否部门资产管理员', compute=compute_assets_officer)
    asset_check = fields.One2many('dtdream.assets.check', 'assets_manage')
    has_label = fields.Selection([('0', '否'), ('1', '是')], string='标签是否粘贴')
    useable = fields.Selection([('0', '否'), ('1', '是')], string='是否可使用', default='1')
    unused = fields.Selection([('0', '否'), ('1', '是')], string='是否闲置', default='0')
    selfcheck_date = fields.Date(string='自盘时间')
    mark = fields.Text(string='备注')

    _sql_constraints = [
        ('bill_num_unique', 'UNIQUE(bill_num)', "资产订单号已存在!"),
        ('asset_code_unique', 'UNIQUE(asset_code)', "资产编码已存在!"),
        ('asset_serial_unique', 'UNIQUE(asset_serial)', "资产串号(SN)已存在!"),
        ('asset_serial_unique', 'CHECK(disprice<=price)', "资产残值必须小于等于资产原值!"),
    ]


class dtdream_start_assets_check(models.Model):
    _name = "dtdream.start.assets.check"

    def create_assets_check_records(self, asset):
        vals = {"name": asset.name.id, "bill_num": asset.bill_num, "asset_code": asset.asset_code,
                "asset_serial": asset.asset_serial, "enable_date": asset.enable_date, "in_use": asset.in_use,
                "asset_name": asset.asset_name.id, "asset_type": asset.asset_type.id, "asset_desc": asset.asset_desc,
                "asset_spec": asset.asset_spec, "store_place": asset.store_place.id, "price": asset.price,
                "disprice": asset.disprice, "quality_place_province": asset.quality_place_province.id,
                "quality_place_city": asset.quality_place_city.id, "quality_date": asset.quality_date,
                "has_label": asset.has_label, "useable": asset.useable, "unused": asset.unused,
                "explain": asset.explain, "supplier": asset.supplier.id, "assets_manage": asset.id, "mark": asset.mark,
                "email_type": json.dumps(["00"])}
        try:
            result = self.env['dtdream.assets.check'].create(vals)
            result.signal_workflow('assets_create')
            asset.message_poss(state=u'启动盘点成功', action=u'启动盘点', approve=asset.name.name)
        except Exception, e:
            asset.message_poss(state=u'启动盘点失败', action=u'启动盘点')

    @api.one
    def btn_start_assets_check(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        assets = self.env['dtdream.assets.management'].browse(active_ids)
        for asset in assets:
            state = [cr.state for cr in self.env['dtdream.assets.check'].search([("asset_code", "=", asset.asset_code)])]
            if "1" in state:
                continue
            self.create_assets_check_records(asset)
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def btn_remind_asset_check(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        assets = self.env['dtdream.assets.check'].browse(active_ids)
        for asset in assets:
            if asset.state != '1':
                continue
            if not asset.email_type:
                email_type = ["01"]
            else:
                email_type = json.loads(asset.email_type)
                if '01' not in email_type:
                    email_type.append('01')
            asset.write({'email_type': json.dumps(email_type)})
        return {'type': 'ir.actions.act_window_close'}







