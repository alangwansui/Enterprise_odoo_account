# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import expression
from openerp.exceptions import AccessError


class dtdream_assets_mac_manage(models.Model):
    _name = "dtdream.assets.mac.manage"
    _inherit = ['mail.thread']

    @api.depends("assets_code")
    def compute_name_department(self):
        for rec in self:
            rec.name = rec.assets_code.name
            rec.department = rec.assets_code.department

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
        return super(dtdream_assets_mac_manage, self).search_read(domain=domain, fields=fields, offset=offset,
                                                             limit=limit, order=order)

    def check_access_mac_manage(self):
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
        result = super(dtdream_assets_mac_manage, self).read(fields=fields, load=load)
        perm_read = self.check_access_mac_manage()
        if load == '_classic_read' and not perm_read:
            raise AccessError('由于安全限制，请求的操作不能被完成。请联系你的系统管理员。' +
                              '\n\n(单据类型: dtdream.assets.mac.manage, 操作: read.)')
        return result

    assets_code = fields.Many2one('dtdream.assets.management', string='资产编码')
    name = fields.Many2one('hr.employee', string='责任人', compute=compute_name_department)
    department = fields.Many2one('hr.department', string='部门', compute=compute_name_department)
    mac_address = fields.Char(string='mac地址', size=16)

    _sql_constraints = [
        ('asset_code_uniquee', 'UNIQUE(asset_code)', "资产编码已存在!"),
        ('asset_mac_address', 'UNIQUE(mac_address)', "MAC地址已存在已存在!"),
    ]
