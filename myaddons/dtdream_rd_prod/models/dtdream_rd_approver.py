# -*- coding: utf-8 -*-
from openerp import models, fields, api

#产品审批基础数据配置
class dtdream_rd_approver(models.Model):
    _name = 'dtdream_rd_approver'
    name = fields.Many2one('dtdream_rd_config',string="角色")
    pro_state = fields.Selection([('state_01','立项'),('state_02','总体设计')],string='阶段')
    level = fields.Selection([('level_01','一级'),('level_02','二级')],string='级别')

    @api.onchange('level')
    def _is_level(self):
        if self.level=='level_01':
            self.is_level=True
        else:
            self.is_level=False

    department = fields.Many2one('hr.department',string='部门')
    is_level = fields.Boolean(string="是否一级", readonly=True)