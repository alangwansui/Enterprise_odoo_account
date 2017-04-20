# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_construction(models.Model):
    _name = 'dtdream.project.construction'

    name = fields.Char(string='姓名', size=8)
    role = fields.Char(string='角色名称', size=16)
    department = fields.Char(string='公司/部门', size=32)
    response = fields.Char(string='职责', size=64)
    tel = fields.Char(string='联系方式', size=16)
    project_manage_id = fields.Many2one('dtdream.project.manage')


class dtdream_project_construction_inner(models.Model):
    _name = 'dtdream.project.construction.inner'

    @api.depends('name')
    def compute_deparment_name(self):
        for rec in self:
            rec.department = rec.name.department_id
            rec.tel = rec.name.mobile_phone

    name = fields.Many2one('hr.employee', string='姓名')
    role = fields.Many2one('dtdream.project.role.setting', string='角色名称')
    department = fields.Many2one('hr.department', string='公司/部门', compute=compute_deparment_name)
    response = fields.Char(string='职责', size=64)
    tel = fields.Char(string='联系方式', size=16)
    project_manage_id = fields.Many2one('dtdream.project.manage')

