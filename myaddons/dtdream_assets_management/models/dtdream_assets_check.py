# -*- coding: utf-8 -*-

from openerp import models, fields, api
from lxml import etree
from openerp.osv import expression


class dtdream_assets_check(models.Model):
    _name = 'dtdream.assets.check'
    _description = u'资产盘点'
    _inherit = ['mail.thread']

    def compute_check_date(self):
        if self.state == "0":
            self.selfcheck_date = False
        else:
            self.selfcheck_date = self.write_date

    @api.depends('name')
    def compute_workid_department(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id

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
        manage = self.env.ref("dtdream_assets_management.dtdream_assets_manage") in self.env.user.groups_id
        if manage:
            domain = domain if domain else []
        else:
            uid = self._context.get('uid', '')
            domain = expression.AND([[('name.user_id', '=', uid)], domain])
        return super(dtdream_assets_check, self).search_read(domain=domain, fields=fields, offset=offset,
                                                             limit=limit, order=order)

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
    supplier = fields.Many2one('dtdream.assets.supply', string='供应商')
    explain = fields.Text(string='说明')
    has_label = fields.Selection([('0', '否'), ('1', '是')], string='标签是否粘贴')
    useable = fields.Selection([('0', '否'), ('1', '是')], string='是否可使用')
    unused = fields.Selection([('0', '否'), ('1', '是')], string='是否闲置')
    mark = fields.Text(string='备注')
    selfcheck_date = fields.Date(string='自盘时间', compute=compute_check_date)
    state = fields.Selection([('0', '未盘点'), ('1', '已盘点')], string='状态', default='0')
    amongst = fields.Boolean(string='是否资产责任人', compute=compute_assets_amongst)
    is_manage = fields.Boolean(string='是否资产管理员', compute=compute_assets_manage)
    assets_manage = fields.Many2one('dtdream.assets.management')

    @api.multi
    def wkf_done(self):
        self.write({"state": '1'})
