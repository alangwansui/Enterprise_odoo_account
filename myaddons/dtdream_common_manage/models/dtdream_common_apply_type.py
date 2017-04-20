# -*- coding: utf-8 -*-
from openerp import models, fields, api


class dtdream_common_apply_type(models.Model):
    _name = "dtdream.common.apply.type"
    _description = u"申请类型"

    type = fields.Char(string=u"申请类型", required=True)
    approver = fields.Many2one(comodel_name="hr.employee", string=u"IT审批人", required=True)
    use_users = fields.Boolean(string=u"是否使用成员", required=True, default=False)
    work = fields.Boolean(string=u"是否有效", required=True, default=True)

    # 显示名称
    @api.multi
    def name_get(self):
        data = []
        for r in self:
            data.append((r.id, r.type))
        return data
