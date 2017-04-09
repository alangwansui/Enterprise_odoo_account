# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
import logging
_logger = logging.getLogger(__name__)


class dtdream_expense_chuchai(models.Model):
    _name = "dtdream.expense.chuchai"

    @api.depends('name')
    def _compute_chuchai_fields(self):
        for rec in self:
            rec.endtime = rec.name.endtime
            rec.startaddress = rec.name.startaddress
            rec.endaddress =rec.name.endaddress
            rec.reason = rec.name.reason

    def _filter_chuchai_record(self):
        return [('create_uid', '=', self.env.user.id)]

    name = fields.Many2one('dtdream.travel.journey', string="出差时间", domain=_filter_chuchai_record)
    report_id = fields.Many2one("dtdream.expense.report", string="报销单ID")
    endtime = fields.Date(string="结束时间", compute=_compute_chuchai_fields)
    startaddress = fields.Char(string="出发地", compute=_compute_chuchai_fields)
    endaddress = fields.Char(string="目的地", compute=_compute_chuchai_fields)
    reason = fields.Text(string="出差原因", compute=_compute_chuchai_fields)

    _sql_constraints = [
        ('chuchai_id_unique', 'UNIQUE(name)', "出差时间重复，请重新选择！")
    ]
