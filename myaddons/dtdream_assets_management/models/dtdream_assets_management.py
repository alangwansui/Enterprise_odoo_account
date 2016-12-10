# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_assets_management(models.Model):
    _name = 'dtdream.assets.management'
    _description = u'资产管理'
    _inherit = ['mail.thread']

    @api.depends('name')
    def compute_workid_department(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id

    def compute_check_record(self):
        self.check_record = len(self.env["dtdream.assets.check"].search([("assets_manage", "=", self.id)]))

    @api.multi
    def message_poss(self, state, action, approve=''):
        self.message_post(body=u"""<table border="1" style="border-collapse: collapse;">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">下一处理人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, approve))

    name = fields.Many2one('hr.employee', string='资产责任人')
    workid = fields.Char(string='工号', compute=compute_workid_department)
    department = fields.Many2one('hr.department', string='部门', compute=compute_workid_department)
    bill_num = fields.Char(string='订单号', size=32)
    asset_code = fields.Char(string='资产编号', size=32)
    asset_serial = fields.Char(string='资产串号(SN)', size=32)
    enable_date = fields.Date(string='启用日期')
    in_use = fields.Date(string='领用日期')
    asset_name = fields.Many2one('dtdream.assets.name', string='资产名称')
    asset_desc = fields.Char(string='资产描述', size=128)
    store_place = fields.Many2one('dtdream.assets.store.place', string='使用地点')
    mac = fields.Char(string='MAC地址', size=16)
    use_state = fields.Selection([('0', '使用中'), ('1', '闲置')], string='使用状态')
    price = fields.Float(string='成本', digits=(10, 2))
    quality_date = fields.Date(string='质保')
    explain = fields.Text(string='说明')
    supplier = fields.Many2one('dtdream.assets.supply', string='供应商')
    check_record = fields.Integer(string='盘点记录', compute=compute_check_record)
    asset_check = fields.One2many('dtdream.assets.check', 'assets_manage')


class dtdream_assets_check_start(models.Model):
    _name = "dtdream.assets.check.start"

    def create_assets_check(self, asset):
        vals = {"name": asset.name.id, "bill_num": asset.bill_num, "asset_code": asset.asset_code,
                "asset_serial": asset.asset_serial, "enable_date": asset.enable_date, "in_use": asset.in_use,
                "asset_name": asset.asset_name.id, "asset_desc": asset.asset_desc, "store_place": asset.store_place.id,
                "mac": asset.mac, "use_state": asset.use_state, "price": asset.price,
                "quality_date": asset.quality_date, "explain": asset.explain, "supplier": asset.supplier.id,
                "assets_manage": asset.id}
        try:
            self.env['dtdream.assets.check'].create(vals)
            asset.message_poss(state=u'启动盘点成功', action=u'启动盘点', approve=asset.name.name)
        except Exception, e:
            asset.message_poss(state=u'启动盘点失败', action=u'启动盘点')

    @api.one
    def start_assets_check(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        assets = self.env['dtdream.assets.management'].browse(active_ids)
        for asset in assets:
            self.create_assets_check(asset)
        return {'type': 'ir.actions.act_window_close'}






