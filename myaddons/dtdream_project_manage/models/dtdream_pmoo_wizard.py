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
        self.update_role_record(project)

    def update_pmoo_value(self, project):
        for rec in project.role:
                if rec.name == u'PMO主管':
                    rec.leader = self.pmo

    def update_role_record(self, project):
        if project.yunwei == '0':
            self.env['dtdream.project.role'].search([('project_manage_id', '=', project.id),
                                                     ('name', '=', u'运维服务经理')]).unlink()

