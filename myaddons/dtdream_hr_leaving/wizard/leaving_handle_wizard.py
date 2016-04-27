# -*- coding: utf-8 -*-

from openerp import models, fields, api

class leaving_handle_wizard(models.TransientModel):
    _name = 'leaving.handle.wizard'

    def _default_manager_id(self):
        active_id = self._context['active_id']
        current_leaving_handle = self.env['leaving.handle'].browse(active_id)
        return current_leaving_handle.department_id.manager_id

    def _default_assistant_id(self):
        active_id = self._context['active_id']
        current_leaving_handle = self.env['leaving.handle'].browse(active_id)
        if(len(current_leaving_handle.department_id.assitant_id) >0):
            return current_leaving_handle.department_id.assitant_id[0]


    name = fields.Char("审批环节")
    result = fields.Selection([("agree","同意"),("reject","驳回到上一步"),("other","不涉及")])
    opinion = fields.Text("意见", required=True)
    actual_leavig_date = fields.Date("实际离岗时间")
    leaving_handle_id = fields.Many2one("leaving.handle",string="离职交接申请")
    current_state = fields.Char("当前环节")
    mail_ccs = fields.Many2many('hr.employee',string="抄送人")
    manager_id = fields.Many2one('hr.employee',string="主管",default=_default_manager_id)
    assistant_id = fields.Many2one('hr.employee',string="行政助理",default=_default_assistant_id)

    @api.one
    def btn_agree(self):
        active_id = self._context['active_id']
        current_leaving_handle = self.env['leaving.handle'].browse(active_id)
        if self.current_state == "4":
            current_leaving_handle.write({"actual_leavig_date":self.actual_leavig_date})
        if self.current_state == "1":
            current_leaving_handle.write({"manager_id": self.manager_id.id})
            current_leaving_handle.write({"assistant_id": self.assistant_id.id})

        self.name = current_leaving_handle.state_dict[current_leaving_handle.state]
        mail_ccs_user_ids = []
        for rec in self.mail_ccs:
            mail_ccs_user_ids.append(rec.id)

        self.env['leaving.handle.approve.record'].create({"name":self.name,"result":"agree", "opinion":self.opinion,
                                                          "leaving_handle_id":active_id,"mail_ccs":[(6, 0, mail_ccs_user_ids)]})
        current_leaving_handle.signal_workflow('btn_agree')

    @api.one
    def btn_reject(self):
        active_id = self._context['active_id']
        current_leaving_handle = self.env['leaving.handle'].browse(active_id)
        if self.current_state == "4":
            current_leaving_handle.write({"actual_leavig_date": self.actual_leavig_date})
        if self.current_state == "1":
            current_leaving_handle.write({"manager_id": self.manager_id.id})
            current_leaving_handle.write({"assistant_id": self.assistant_id.id})
        self.name = current_leaving_handle.state_dict[current_leaving_handle.state]
        mail_ccs_user_ids = []
        for rec in self.mail_ccs:
            mail_ccs_user_ids.append(rec.id)
        self.env['leaving.handle.approve.record'].create({"name":self.name,"result":"reject", "opinion":self.opinion,
                                                          "leaving_handle_id":active_id,"mail_ccs":[(6, 0, mail_ccs_user_ids)]})
        current_leaving_handle.signal_workflow('btn_reject')

    @api.one
    def btn_other(self):
        active_id = self._context['active_id']
        current_leaving_handle = self.env['leaving.handle'].browse(active_id)
        if self.current_state == "4":
            current_leaving_handle.write({"actual_leavig_date": self.actual_leavig_date})
        if self.current_state == "1":
            current_leaving_handle.write({"manager_id": self.manager_id.id})
            current_leaving_handle.write({"assistant_id": self.assistant_id.id})
        self.name = current_leaving_handle.state_dict[current_leaving_handle.state]
        mail_ccs_user_ids = []
        for rec in self.mail_ccs:
            mail_ccs_user_ids.append(rec.id)
        self.env['leaving.handle.approve.record'].create({"name": self.name, "result": "other", "opinion": self.opinion,
                                                          "leaving_handle_id": active_id,"mail_ccs":[(6, 0, mail_ccs_user_ids)]})
        current_leaving_handle.signal_workflow('btn_agree')
