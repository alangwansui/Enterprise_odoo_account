# -*- coding: utf-8 -*-
from openerp import models, fields, api

class view(models.Model):
    _inherit = 'ir.ui.view'

    type= fields.Selection([
        ('tree', 'Tree'),
        ('form', 'Form'),
        ('graph', 'Graph'),
        ('pivot', 'Pivot'),
        ('calendar', 'Calendar'),
        ('diagram', 'Diagram'),
        ('gantt', 'Gantt'),
        ('kanban', 'Kanban'),
        ('sales_team_dashboard', 'Sales Team Dashboard'),
        ('expense_dashboard', 'expense_dashboard'),
        ('rd_dashboard', 'rd_dashboard'),
        ('dtdream_pay_dashboard', 'dtdream_pay_dashboard'),
        ('remand_dashboard', 'remand_dashboard'),
        ('search', 'Search'),
        ('qweb', 'QWeb')], string='View Type')

class dtdream_remand_dashboard(models.Model):
    _name = 'dtdream.remand.dashboard'
    _description = u"仪表盘"

    @api.model
    def retrieve_remand_dashboard(self):
        res = {
            "group_number": 0,
            "demand_number": 0
        }
        em = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if em:
            group_ids = self.env['dtdream.ad.group'].search(['|', ('admins', '=', em[0].id), ('users', '=', em[0].id)])
            demand_ids = self.env['dtdream.demand.app'].search([('name', '=', em[0].id)])
            if group_ids:
                res['group_number'] = len(group_ids)
            if demand_ids:
                res['demand_number'] = len(demand_ids)
        return res

