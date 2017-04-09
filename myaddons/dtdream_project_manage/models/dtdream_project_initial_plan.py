# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_initial_plan(models.Model):
    _name = 'dtdream.project.initial.plan'

    plan = fields.Date(string='项目计划')
    design = fields.Date(string='实施方案')
    deliver = fields.Date(string='平台交付')
    yunwei = fields.Date(string='运维')
    check = fields.Date(string='初验')
    check_final = fields.Date(string='终验')
    project_manage_id = fields.Many2one('dtdream.project.manage')
