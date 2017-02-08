# -*- coding: utf-8 -*-

from openerp import models, fields


class dtdream_expense_operation_management(models.Model):
    _name = "dtdream.expense.operation.management"
    _description = u"关联配置"
    name = fields.Selection([('budget', '关联预算部门'), ('project', '关联项目部门')], string='类别')
    dep_name = fields.Many2many('hr.department', 'dtdream_expense_yunying_department',string='部门')

    _sql_constraints = [('name_unique', 'unique(name)', '类别是唯一的！')]
