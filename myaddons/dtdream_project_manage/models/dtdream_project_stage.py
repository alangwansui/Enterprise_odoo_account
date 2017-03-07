# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_stage(models.Model):
    _name = 'dtdream.project.stage'

    name = fields.Char('阶段名称', size=8)
    plan_start_time = fields.Date(string='计划开始时间')
    plan_end_time = fields.Date(string='计划结束时间')
    fact_start_time = fields.Date(string='实际开始时间')
    fact_end_time = fields.Date(string='实际结束时间')
    project_manage_id = fields.Many2one('dtdream.project.manage')


class dtdream_project_stage_setting(models.Model):
    _name = 'dtdream.project.stage.setting'

    name = fields.Char('阶段名称', size=8)
    order = fields.Integer(string='序号')

