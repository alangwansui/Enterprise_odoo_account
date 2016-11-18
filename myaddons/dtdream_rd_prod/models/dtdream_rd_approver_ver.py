#-*- coding: UTF-8 -*-
from openerp import models, fields, api


#版本审批基础数据配置
class dtdream_rd_approver_ver(models.Model):
    _name = 'dtdream_rd_approver_ver'
    name = fields.Many2one('dtdream_rd_config',string="角色")
    ver_state = fields.Selection([('initialization','计划中'),('Development','开发中'),('pending','待发布')],string='阶段')
    level = fields.Selection([('level_01','一级'),('level_02','二级')],string='级别')
    department = fields.Many2one('hr.department','部门')
    is_formal = fields.Boolean(string="是否为正式版本")

    @api.onchange('ver_state')
    def get_is_pending(self):
        if self.ver_state=='pending':
            self.is_pending=True
        else:
            self.is_pending=False

    is_pending = fields.Boolean("是否待发布")

    @api.onchange('level')
    def _is_level(self):
        if self.level=='level_01':
            self.is_level=True
        else:
            self.is_level=False

    is_level = fields.Boolean( string="是否一级",readonly=True)