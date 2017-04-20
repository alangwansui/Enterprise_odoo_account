# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
class shenpi_text(models.Model):
    _name = "dtdream.shenpi.text"
    _order = "create_date desc"

    shenpi_text_id = fields.Many2one("dtdream.project.bid.authorize.apply")
    content = fields.Char(string="审批意见")
    shenpiren = fields.Many2one("hr.employee",string="审批人")
    # time = fields.Datetime("审批时间", required=True, default=lambda self: datetime.now())

    state = fields.Char("审批阶段")
    res = fields.Char("结果")