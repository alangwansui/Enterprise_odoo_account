# -*- coding: utf-8 -*-

from openerp import models, fields


class dtdream_expense_operation_management(models.Model):
    _name = "dtdream.expense.operation.management"
    _description = u"运营管理体系"
    name = fields.Char(string='name',default='运营管理体系')
    dep_name = fields.Many2many('hr.department','dtdream_expense_yunying_department',string='运营管理体系')
