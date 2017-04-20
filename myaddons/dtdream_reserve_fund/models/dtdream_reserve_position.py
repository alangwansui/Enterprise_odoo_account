# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_reserve_position(models.Model):
    _name = 'dtdream.reserve.position'
    _description = u'备用金职位'

    name = fields.Selection([(u'总裁', '总裁'),
                             (u'接口会计', '接口会计'),
                             (u'出纳会计', '出纳会计')], string='职位')
    employee = fields.Many2one('hr.employee', string='员工')