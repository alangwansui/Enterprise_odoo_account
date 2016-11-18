# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from datetime import date,datetime


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
        ('search', 'Search'),
        ('qweb', 'QWeb')], string='View Type')


class dtdream_rd_dashboard(models.Model):
    _name = 'dtdream.rd.dashboard'

    @api.model
    def retrieve_sales_dashboard(self):
        res={

            "submit_product":0,
            "wait_product":0,
            "my_product": 0,

            "submit_version": 0,
            "wait_version": 0,
            "my_version": 0,

            "submit_exception": 0,
            "wait_exception": 0,
            "my_exception": 0,

            "submit_replanning": 0,
            "wait_replanning": 0,
            "my_replanning": 0
        }
        return res