# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_plan_config(models.Model):
    _name = 'dtdream.project.plan.config'

    name = fields.Many2one('dtdream.project.stage.setting', string='项目阶段')
    plan = fields.One2many('dtdream.project.plan.detail', 'project_stage_id')

    _sql_constraints = [
        ('project_name', 'UNIQUE(name)', "项目阶段已存在!"),
    ]


class dtdream_project_plan_detail(models.Model):
    _name = 'dtdream.project.plan.detail'

    name = fields.Char(string='项目阶段', size=8)
    work_item = fields.Char(string='工作事项', size=20)
    leader = fields.Selection([('1', '项目经理'), ('2', '办事处'), ('3', '总部'), ('4', '驻场')], string='责任人')
    work_details = fields.Text(string='工作说明')
    start_time = fields.Date(string='开始时间')
    end_time = fields.Date(string='结束时间')
    header = fields.Many2one('hr.employee', string='负责人')
    days = fields.Integer(string='预计天数')
    project_stage_id = fields.Many2one('dtdream.project.plan.config', '项目阶段')
    project_manage_id = fields.Many2one('dtdream.project.manage', string='项目')
    can_delete = fields.Boolean(string='是否可以删除')
