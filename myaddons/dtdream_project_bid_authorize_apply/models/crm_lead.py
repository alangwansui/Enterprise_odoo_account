# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp .exceptions import ValidationError

class dtdream_crm_lead(models.Model):
    _inherit = 'crm.lead'

    authorization_count = fields.Integer(string="项目授权数量",default=0,readonly=True)
    has_draft_authorization = fields.Boolean(default=False,string="项目授权是否已经存在")

    @api.multi
    def action_dtdream_project_authorization(self):
        # if self.business_count == 0:
        #     if self.sale_apply_id.user_id.id != self._uid:
        #         raise ValidationError("只有营销责任人可以创建对应商务报备申请。")
        # if not self.env['crm.lead'].search([('id','=', self.id)]):
        #     raise ValidationError("项目已归档，无法创建商务报备申请")
        cr = self.env['dtdream.project.bid.authorize.apply'].search([('rep_pro_name.id', '=', self.id)],order='create_date desc',limit=1)
        res_id = cr.id if cr else ''
        import json
        context = json.loads(json.dumps(self._context))
        context.update({'active_id': self.id})
        action = {
            'name': '项目授权',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dtdream.project.bid.authorize.apply',
            'res_id': res_id,
            'context': context,
            }
        return action