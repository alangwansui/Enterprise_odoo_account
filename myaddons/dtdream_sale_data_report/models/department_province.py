# -*- coding: utf-8 -*-

from openerp import models, fields, api

class department_province(models.Model):
    _name = 'department.province'

    name = fields.Many2one('sale.department',related='sale_department')

    sale_project_province = fields.Many2many("dtdream.area",string='省份',required=True,domain=[('parent_id','=',False)])

    sale_department = fields.Many2one('sale.department', string='部门',required=True)

class sale_department(models.Model):
    _name = 'sale.department'

    name = fields.Char("部门名称")