# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_pmoo_wizard(models.TransientModel):
    _name = 'dtdream.pmoo.wizard'

    @api.depends('pmo', 'vip')
    def compute_project_state_y(self):
        project = self.env['dtdream.project.manage'].browse(self._context['active_id'])
        self.state_y = project.state_y

    pmo = fields.Many2one('hr.employee', string="PMO主管")
    vip = fields.Many2one('hr.employee', string='VIP经理')
    state_y = fields.Char(string='状态', compute=compute_project_state_y)

    @api.one
    def btn_confirm(self):
        project = self.env['dtdream.project.manage'].browse(self._context['active_id'])
        if self.state_y == '0':
            self.update_pmoo_value(project)
        elif self.state_y == '33':
            project.current_approve = [(6, 0, [self.vip.id])]
        project.signal_workflow('btn_submit')

    def update_pmoo_value(self, project):
        for rec in project.role:
                if rec.name == self.env.ref('dtdream_project_manage.dtdream_project_role_PMOO').name:
                    rec.leader = self.pmo
                if rec.name == self.env.ref('dtdream_project_manage.dtdream_project_role_PMO').name:
                    rec.leader = project.create_uid.employee_ids

