# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.osv import expression
from openerp.exceptions import AccessError
from lxml import etree


class dtdream_assets_management(models.Model):
    _name = 'dtdream.assets.management'
    _description = u'资产管理'
    _rec_name = 'asset_code'
    _inherit = ['mail.thread']

    @api.depends('name')
    def compute_workid_department(self):
        for rec in self:
            rec.workid = rec.name.job_number
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

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(dtdream_assets_management, self).read(fields=fields, load=load)
        perm_read = self.check_access_assets_manage()
        if load == '_classic_read' and not perm_read:
            raise AccessError('由于安全限制，请求的操作不能被完成。请联系你的系统管理员。' +
                              '\n\n(单据类型: dtdream.assets.management, 操作: read.)')
        return result

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
                "explain": asset.explain, "supplier": asset.supplier.id, "assets_manage": asset.id, "mark": asset.mark}
        try:
            self.env['dtdream.assets.check'].create(vals).signal_workflow('assets_create')
            asset.message_poss(state=u'启动盘点成功', action=u'启动盘点', approve=asset.name.name)
        except Exception, e:
            asset.message_poss(state=u'启动盘点失败', action=u'启动盘点')

    @api.one
    def btn_start_assets_check(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        assets = self.env['dtdream.assets.management'].browse(active_ids)
        email_from, url = self.get_assets_check_email_url()
        checks = {}
        for asset in assets:
            self.create_assets_check_records(asset)
            if not checks.has_key(asset.name.work_email):
                checks[asset.name.work_email] = {"name": asset.name.name,
                                                 "email": asset.name.work_email,
                                                 "subject": u'资产盘点已启动,请完成盘点工作',
                                                 "text": u'资产盘点工作已启动,请对自己名下的资产信息进行盘点。资产信息如下:',
                                                 "email_from": email_from,
                                                 'date': datetime.now().strftime('%Y-%m-%d'),
                                                 "content": [(u"<tr><td>{0}</td><td>{1}</td><td>" +
                                                             u"<a href={2}>点击自盘</a></td></tr>").format(
                                                            asset.asset_name.name, asset.asset_code, url) % asset.id]}
            else:
                item = u"<tr><td>{0}</td><td>{1}</td><td><a href={2}>点击自盘</a></td></tr>".format(
                    asset.asset_name.name, asset.asset_code, url) % asset.id
                checks[asset.name.work_email]["content"].append(item)
        self.btn_send_email(checks)
        return {'type': 'ir.actions.act_window_close'}

    def get_assets_check_email_url(self):
        check = self.env['dtdream.assets.check']
        email_from = check.get_mail_server_name()
        base_url = check.get_base_url()
        menu_id, action = check.get_assets_check_menu()
        url = '%s/web#id=%%s&view_type=form&model=dtdream.assets.check&action=%s&menu_id=%s' % (base_url, action, menu_id)
        return email_from, url

    def btn_send_email(self, checks):
        for check in checks.values():
            email_to = check.get('email')
            appellation = u'{0},您好：'.format(check.get('name'))
            subject = check.get('subject')
            content = check.get('content')
            self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                    <p>%s</p>
                                    <p>
                                    <table border="1"><tr style="font-weight:bold;height:40px">
                                    <td width="120px;">资产名称</td>
                                    <td width="240px;">资产编号</td>
                                    <td>盘点链接</td>
                                    </tr>%s</table>
                                    </p>
                                    <p>dodo</p>
                                    <p>万千业务，简单有do</p>
                                    <p>%s</p>''' % (appellation, check.get('text'), ''.join(content), check.get('date')),
                    'subject': '%s' % subject,
                    'email_from': check.get('email_from'),
                    'email_to': '%s' % email_to,
                    'auto_delete': False,
                }).send()

    @api.one
    def btn_remind_asset_check(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        assets = self.env['dtdream.assets.check'].browse(active_ids)
        email_from, url = self.get_assets_check_email_url()
        checks = {}
        for asset in assets:
            if asset.state != '1':
                continue
            if not checks.has_key(asset.name.work_email):
                checks[asset.name.work_email] = {"name": asset.name.name,
                                                 "email": asset.name.work_email,
                                                 "subject": u'您名下存在未盘点的资产,请尽快完成盘点工作',
                                                 "text": u'您名下存在未盘点的资产,请尽快完成盘点。资产信息如下:',
                                                 "email_from": email_from,
                                                 'date': datetime.now().strftime('%Y-%m-%d'),
                                                 "content": [(u"<tr><td>{0}</td><td>{1}</td><td>" +
                                                             u"<a href={2}>点击自盘</a></td></tr>").format(
                                                            asset.asset_name.name, asset.asset_code, url) % asset.id]}
            else:
                item = u"<tr><td>{0}</td><td>{1}</td><td><a href={2}>点击自盘</a></td></tr>".format(
                    asset.asset_name.name, asset.asset_code, url) % asset.id
                checks[asset.name.work_email]["content"].append(item)
        self.btn_send_email(checks)
        return {'type': 'ir.actions.act_window_close'}







