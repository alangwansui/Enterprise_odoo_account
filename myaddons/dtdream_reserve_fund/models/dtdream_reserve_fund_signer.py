# -*- coding: utf-8 -*-
from openerp import models, fields


class dtdream_reserve_fund_signer(models.Model):
    _name = 'dtdream.reserve.fund.signer'
    _description = u'备用金权签人'
    name = fields.Many2one('hr.employee', string='员工')
    type = fields.Selection([(u'行政类', '行政类'),
                             (u'专项类', '专项类'),
                             (u'常用备用金', '常用备用金'),
                             (u'公有云项目', '公有云项目'),
                             (u'其他', '其他'),
                             (u'非专项类', '非专项类'),
                             (u'所有', '所有')],
                            string='审批的备用金类型')
    dtdream_reserve_fund_id1 = fields.Many2one('hr.department', string='第一权签人部门')
    dtdream_reserve_fund_id2 = fields.Many2one('hr.department', string='第二权签人部门')