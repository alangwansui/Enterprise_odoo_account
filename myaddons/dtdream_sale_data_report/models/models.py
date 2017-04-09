# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp .exceptions import ValidationError

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
        areas = self.get_departments_selections()
        return {'cash_income_sum':99999,'areas':areas}

    @api.model
    def get_departments_selections(self):
        department_list = self.env['sale.department'].sudo().search([])
        departments = [rec.name for rec in department_list]
        return departments

    @api.model
    def get_province_by_department(self,dep_name):
        pro_rec = self.env['department.province'].sudo().search([('sale_department.name','=',dep_name)])
        if len(pro_rec) == 1:
            pro_list = pro_rec.sale_project_province
            provinces = [rec.name for rec in pro_list]
            return provinces
        else:
            return

    @api.model
    def get_cash_income_sum(self):
        return self.env['crm.lead']

    @api.model
    def get_echart_data(self):
        office_ids = self.env['dtdream.office'].sudo().search([])
        office_names = [rec.name for rec in office_ids]
        return {'office_names':office_names}