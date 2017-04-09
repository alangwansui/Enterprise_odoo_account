# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_construction(models.Model):
    _name = 'dtdream.project.construction'

    name = fields.Char(string='姓名', size=8)
    role = fields.Char(string='角色名称', size=16)
    department = fields.Char(string='公司/部门', size=32)
    response = fields.Char(string='职责', size=64)
    project_manage_id = fields.Many2one('dtdream.project.manage')
