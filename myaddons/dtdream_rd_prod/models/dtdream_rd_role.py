# -*- coding: utf-8 -*-
from openerp import models, fields, api


#产品里的人员
class dtdream_rd_role(models.Model):
    _name = 'dtdream_rd_role'
    # _rec_name ="person"
    role_id = fields.Many2one("dtdream_prod_appr")
    cof_id = fields.Many2one('dtdream_rd_config', string="角色")
    person = fields.Many2one("hr.employee",'人员')

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

    @api.multi
    def name_get(self):
        res = super(dtdream_rd_role, self).name_get()
        data = []
        for role in self:
            display_value = ''
            display_value += role.cof_id.name or ""
            display_value += ' '
            display_value += role.person.name or ""
            data.append((role.id, display_value))
        return data

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, ['|',('cof_id', 'ilike', name),('person', 'ilike', name)] + args, limit=limit)
        return super(dtdream_rd_role, self).name_search(
            cr, user, '', args=[('id', 'in', list(ids))],
            operator='ilike', context=context, limit=limit)