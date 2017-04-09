# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_pmoo_wizard(models.TransientModel):
    _name = 'dtdream.pmoo.wizard'

    pmo = fields.Many2one('hr.employee', string="PMO主管")

    @api.one
    def btn_confirm(self):
        project = self.env['dtdream.project.manage'].browse(self._context['active_id'])
        self.update_pmoo_value(project)
        project.signal_workflow('btn_submit')

    def update_pmoo_value(self, project):
        for rec in project.role:
                if rec.name == self.env.ref('dtdream_project_manage.dtdream_project_role_PMOO').name:
                    rec.leader = self.pmo
                if rec.name == self.env.ref('dtdream_project_manage.dtdream_project_role_PMO').name:
                    rec.leader = project.create_uid.employee_ids

