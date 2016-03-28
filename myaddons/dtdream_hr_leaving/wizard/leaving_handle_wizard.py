# -*- coding: utf-8 -*-

from openerp import models, fields, api

class leaving_handle_wizard(models.TransientModel):
    _name = 'leaving.handle.wizard'

    name = fields.Char("审批环节")
    result = fields.Selection([("agree","同意"),("reject","驳回"),("other","不涉及")])
    opinion = fields.Text("意见", required=True)
    leaving_handle_id = fields.Many2one("leaving.handle",string="离职交接申请")

    @api.one
    def btn_agree(self):
        active_id = self._context['active_id']
        current_leaving_handle = self.env['leaving.handle'].browse(active_id)
        self.name = current_leaving_handle.state_dict[current_leaving_handle.state]
        self.create({"name":self.name,"result":"agree", "opinion":self.opinion,"leaving_handle_id":active_id})
        current_leaving_handle.signal_workflow('btn_agree')

    @api.one
    def btn_reject(self):
        active_id = self._context['active_id']
        current_leaving_handle = self.env['leaving.handle'].browse(active_id)
        self.name = current_leaving_handle.state_dict[current_leaving_handle.state]
        self.create({"name":self.name,"result":"reject", "opinion":self.opinion,"leaving_handle_id":active_id})
        current_leaving_handle.signal_workflow('btn_reject')