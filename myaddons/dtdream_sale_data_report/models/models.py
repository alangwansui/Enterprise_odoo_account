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
        ('dtdream_sale_data_report','dtdream_sale_data_report'),
        ('search', 'Search'),
        ('qweb', 'QWeb')], string='View Type')

class dtdream_sale_data_report(models.Model):
    _name = "dtdream.sale.data.report"

    @api.model
    def get_sales_report_data(self):
        cash_income_sum = self.get_cash_income_sum()
        areas = self.get_pro_selections()
        return {'cash_income_sum':99999,'areas':areas}

    @api.model
    def get_pro_selections(self):
        area_list = self.env['dtdream.office'].sudo().search([])
        areas = [rec.name for rec in area_list]
        return areas

    @api.model
    def get_cash_income_sum(self):
        return self.env['crm.lead']

    @api.model
    def get_echart_data(self):
        office_ids = self.env['dtdream.office'].sudo().search([])
        office_names = [rec.name for rec in office_ids]
        return {'office_names':office_names}