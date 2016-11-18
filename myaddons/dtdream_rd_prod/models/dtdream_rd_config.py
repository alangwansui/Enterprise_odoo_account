# -*- coding: utf-8 -*-
from openerp import models, fields, api


#角色基础配置
class dtdream_rd_config(models.Model):
    _name = 'dtdream_rd_config'
    name = fields.Char('角色名称')
    person = fields.Many2one("hr.employee",'人员')
    cof_ids = fields.One2many('dtdream_rd_role','cof_id')
    @api.model
    def _compute_is_Qa(self):
        users = self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users
        ids = []
        for user in users:
            ids+=[user.id]
        if self.env.user.id in ids:
            self.is_Qa = True
        else:
            self.is_Qa=False
    is_Qa = fields.Boolean(string="是否在QA组", compute=_compute_is_Qa, readonly=True)
