# -*- coding: utf-8 -*-

from openerp import models, fields, api

class leaving_handle_process_wizard(models.TransientModel):
    _name = 'leaving.handle.process.wizard'

    name = fields.Char("审批环节")
    opinion = fields.Text("意见", required=True)

    # 根据当前离职环节计算出当前离职申请
    def get_current_leaving_handle(self,current_leaving_handle_process):
        current_leaving_handle = current_leaving_handle_process.leaving_handle_id1
        if len(current_leaving_handle) == 0:
            current_leaving_handle = current_leaving_handle_process.leaving_handle_id2
        return current_leaving_handle

    @api.multi
    def btn_agree(self):
        active_id = self._context['active_id']
        current_leaving_handle_process = self.env['leaving.handle.process'].browse(active_id)
        current_leaving_handle_process.write({"remark":self.opinion, "is_finish":True,"is_other":False})
        current_leaving_handle = self.get_current_leaving_handle(current_leaving_handle_process)
        self.env['leaving.handle.approve.record'].create({"name": current_leaving_handle_process.process_id.name, "result": "finish", "opinion": self.opinion,
                                                          "leaving_handle_id": current_leaving_handle.id})
        origin_state = current_leaving_handle.state
        current_leaving_handle.signal_workflow('btn_submit')
        if origin_state != current_leaving_handle.state:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }


    @api.multi
    def btn_reject(self):
        active_id = self._context['active_id']
        current_leaving_handle_process = self.env['leaving.handle.process'].browse(active_id)
        current_leaving_handle = self.get_current_leaving_handle(current_leaving_handle_process)
        self.name = current_leaving_handle.state_dict[current_leaving_handle.state]
        self.env['leaving.handle.approve.record'].create(
            {"name": self.name, "result": "reject", "opinion": self.opinion,
             "leaving_handle_id": current_leaving_handle.id})
        current_leaving_handle.signal_workflow('btn_reject')
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.multi
    def btn_other(self):
        active_id = self._context['active_id']
        current_leaving_handle_process = self.env['leaving.handle.process'].browse(active_id)
        current_leaving_handle_process.write({"remark": self.opinion, "is_other": True,"is_finish": False})
        current_leaving_handle = self.get_current_leaving_handle(current_leaving_handle_process)
        self.env['leaving.handle.approve.record'].create({"name": current_leaving_handle_process.process_id.name, "result": "other", "opinion": self.opinion,
                                                          "leaving_handle_id": current_leaving_handle.id})
        origin_state = current_leaving_handle.state
        current_leaving_handle.signal_workflow('btn_submit')
        if origin_state != current_leaving_handle.state:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }


