# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_role(models.Model):
    _name = 'dtdream.project.role'

    @api.depends('name')
    def compute_project_state(self):
        for rec in self:
            rec.state = rec.project_manage_id.state_y

    name = fields.Char(string='角色名称', size=16)
    leader = fields.Many2one('hr.employee', string='负责人')
    leader_history = fields.Many2many('hr.employee', string='历史负责人列表')
    required = fields.Selection([('0', '非必填'), ('1', '必填')], string='是否必填')
    state = fields.Selection([('0', '草稿'),
                              ('10', 'PMO主管'),
                              ('11', '项目经理'),
                              ('12', '交付服务经理'),
                              ('13', '发布章程'),
                              ('1', '已立项'),
                              ('20', '发起策划'),
                              ('21', 'PMO审核策划'),
                              ('2', '已策划'),
                              ('3', '已交付'),
                              ('4', '已运维'),
                              ('99', '结项')], string='状态', compute=compute_project_state)
    project_manage_id = fields.Many2one('dtdream.project.manage')


class dtdream_project_role_setting(models.Model):
    _name = 'dtdream.project.role.setting'

    name = fields.Char(string='角色名称', size=16)
    required = fields.Selection([('0', '非必填'), ('1', '必填')])
