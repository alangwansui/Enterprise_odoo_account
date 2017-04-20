# -*- coding: utf-8 -*-

from openerp import models, fields


# 备用金权签设置
class dtdream_reserve_fund_sign(models.Model):
    _inherit = 'hr.department'

    reserve_first_signer = fields.One2many("dtdream.reserve.fund.signer",
                                           'dtdream_reserve_fund_id1',
                                           string="备用金第一权签人",
                                           track_visibility='onchange')
    reserve_first_amount = fields.Integer(string="第一权签人金额", track_visibility='onchange')
    reserve_second_signer = fields.One2many("dtdream.reserve.fund.signer",
                                            'dtdream_reserve_fund_id2',
                                            string="备用金第二权签人",
                                            track_visibility='onchange')
    reserve_second_amount = fields.Integer(string="第二权签人金额", track_visibility='onchange')
    interface_account = fields.Many2one("hr.employee", string="接口会计", track_visibility='onchange')
    cashier = fields.Many2one("hr.employee", string="出纳会计", track_visibility='onchange')
