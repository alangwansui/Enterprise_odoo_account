# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp


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
        ('search', 'Search'),
        ('qweb', 'QWeb')], string='View Type')




class dtdream_expense_report_count(models.Model):
    _name = "dtdream.expense.report.dashboard"

    @api.model
    def retrieve_sales_dashboard(self):
        res={
            "no_expense_report":0,
            "draft_report":0,
            "wait_confirm_report":0,
            "have_check_report":0,
            "override_report":0,
            "override_report_amount":0,
            "have_pay_report":0,
        }

        res['no_expense_report']=self.env['dtdream.expense.record'].search_count([('report_ids','=',False),('create_uid','=',self.env.user.id)])
        res['draft_report']=self.env['dtdream.expense.report'].search_count([('state','=','draft'),('create_uid','=',self.env.user.id)])
        res['waite_confirm_report'] = self.env['dtdream.expense.report'].search_count([('currentauditperson_userid','=',self.env.user.id)])
        res['have_check_report'] = self.env['dtdream.expense.report'].search_count(
            [('hasauditor.user_id', '=', self.env.user.id)])
        res['have_pay_report'] = self.env['dtdream.expense.report'].search_count(
            [('create_uid', '=', self.env.user.id),('state','=','yifukuan')])

        report_ids=self.env['dtdream.expense.report'].search([('is_outtime','=',True),('create_uid','=',self.env.user.id)])

        if report_ids:
            res['override_report']=len(report_ids)
            for report in report_ids:
                res['override_report_amount']+=report.outtime_amount
        return res