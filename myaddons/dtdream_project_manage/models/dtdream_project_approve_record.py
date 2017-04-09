# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_approve_record(models.Model):
    _name = 'dtdream.project.approve.record'

    output = fields.Char(string='输出/交付物名称')
    result = fields.Char(string='审批意见')
    approve = fields.Char(string='审批人')
    approve_time = fields.Datetime(string='审批时间')
    project_manage_id = fields.Many2one('dtdream.project.manage', string='项目')
    output_plan_id = fields.Many2one('dtdream.project.output.plan.manage', string='输出物规划')
    output_deliver_id = fields.Many2one('dtdream.project.output.deliver', string='交付物规划')


