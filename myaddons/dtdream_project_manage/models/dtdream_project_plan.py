# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import AccessError


class dtdream_project_plan_config(models.Model):
    _name = 'dtdream.project.plan.config'

    name = fields.Many2one('dtdream.project.stage.setting', string='项目阶段')
    project_type = fields.Many2one('dtdream.project.type', string='项目类型')
    plan = fields.One2many('dtdream.project.plan.detail', 'project_stage_id')

    _sql_constraints = [
        ('project_name_type_unique', 'UNIQUE(name, project_type)', "项目阶段已存在!"),
    ]


class dtdream_project_plan_detail(models.Model):
    _name = 'dtdream.project.plan.detail'
    _order = 'name'

    @api.model
    def create(self, vals):
        project_id = vals.get('project_manage_id', '')
        if project_id:
            cr = self.env['dtdream.project.manage'].search([('id', '=', project_id)])
            if cr and cr.state_y != '20' and not cr.is_manage:
                raise AccessError('项目规划只有在策划阶段且是项目经理才可新增项。')
            if vals:
                vals.update({'created': True})
        return super(dtdream_project_plan_detail, self).create(vals)

    @api.depends('is_project_manage')
    def compute_project_state(self):
        for rec in self:
            rec.state_y = rec.project_manage_id.state_y

    def compute_is_manage(self):
        for rec in self:
            rec.is_project_manage = rec.project_manage_id.is_project_manage

    def compute_is_admin(self):
        for rec in self:
            rec.is_manage = rec.project_manage_id.is_manage

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.can_delete and not rec.is_manage:
                raise AccessError('此项为必须项不可删除!')
            if rec.state_y != '20' and rec.is_manage:
                raise AccessError('无法删除此项!')
        return super(dtdream_project_plan_detail, self).unlink()

    name = fields.Many2one('dtdream.project.stage.setting', string='项目阶段')
    work_item = fields.Char(string='工作事项', size=20)
    leader = fields.Selection([('1', '项目经理'), ('2', '办事处'), ('3', '总部'), ('4', '驻场')], string='责任人')
    work_details = fields.Text(string='工作说明')
    start_time = fields.Date(string='开始时间')
    end_time = fields.Date(string='结束时间')
    header = fields.Many2one('hr.employee', string='负责人')
    days = fields.Integer(string='预计人天')
    project_stage_id = fields.Many2one('dtdream.project.plan.config', '项目策划')
    project_manage_id = fields.Many2one('dtdream.project.manage', string='项目')
    can_delete = fields.Boolean(string='是否必须')
    created = fields.Boolean(string='是否已创建')
    is_project_manage = fields.Boolean(string='是否项目经理', compute=compute_is_manage)
    is_manage = fields.Boolean(string='是否管理员', compute=compute_is_admin)
    state_y = fields.Selection([('0', '草稿'),
                               ('10', '指派项目经理'),
                               ('11', '同步项目订单信息'),
                               ('12', '交付服务经理确认'),
                               ('1', '立项'),
                               ('20', '发起策划'),
                               ('21', 'PMO审核策划'),
                               ('2', '策划'),
                               ('3', '交付'),
                               ('30', '运维管控测试'),
                               ('31', '交付运维测试'),
                               ('32', '运维服务经理审核'),
                               ('33', '指定VIP经理'),
                               ('34', 'VIP经理确认'),
                               ('4', '运维'),
                               ('99', '结项')], string='项目状态', compute=compute_project_state)




