# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime,time
from openerp .exceptions import ValidationError,Warning
import time


import logging
_logger = logging.getLogger(__name__)


#权签授权模型
class dtdream_expense_quanqian(models.Model):
    _inherit = 'hr.department'

    def _compute_expense_admin(self):
        for rec in self:
            if rec.env.ref('dtdream_expense.group_dtdream_expense_admin') in rec.env.user.groups_id:
                rec.is_expense_admin = True
            else:
                rec.is_expense_admin = False

    no_one_auditor = fields.Many2one("hr.employee", string="第一审批人", help="正常情况下是二级部门主管。",track_visibility='onchange')
    no_one_auditor_amount = fields.Integer(string="第一审批人权签金额",track_visibility='onchange')
    no_two_auditor = fields.Many2one("hr.employee",string="第二审批人",help="正常情况下是一级部门主管。",track_visibility='onchange')
    no_two_auditor_amount = fields.Integer(string="第二审批人权签金额",track_visibility='onchange')
    no_three_auditor = fields.Many2one("hr.employee",string="第三审批人",help="正常情况下是公司级权力最大的总裁，该字段预留，暂时不用，请到配置处获取总裁信息。",track_visibility='onchange')

    jiekoukuaiji = fields.Many2one("hr.employee",string="接口会计",track_visibility='onchange')
    chunakuaiji = fields.Many2one("hr.employee", string="出纳会计",track_visibility='onchange')
    is_expense_admin = fields.Boolean(string="是否财务业务管理员",compute=_compute_expense_admin)

